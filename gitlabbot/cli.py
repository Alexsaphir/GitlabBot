import re
from pathlib import Path
from typing import Literal

import gitlab
from gitlab.v4.objects import ProjectMergeRequest, ProjectMergeRequestNote
from loguru import logger

from gitlabbot import Settings

modes = {
        'hr': 'HelmRelease',
        'ks': 'Kustomization', }


def clean_diff(lines: list[str]) -> str:
    lines[1] = ''
    lines[3] = ''
    lines[5] = ''

    return ''.join(lines)


def clean_dyff(lines: list[str]) -> str:

    # delete first blank line
    if lines[0] == '\n':
        lines[0] = ''

    return re.sub(r'\n{3,}=(.*?)\n=(.*?)\n#(.*?)\n',
                  r'\n\n=\1\n=\2\n#\3\n',
                  ''.join(lines)).lstrip('\n').rstrip('\n')


def create_content(diff_file: Path, mode: Literal['hr', 'ks'], guard_str: str) -> str:
    with open(diff_file, 'r') as f:
        diff = f.readlines()

    diff = clean_dyff(diff)

    return f'{guard_str}\n# {modes[mode]}\n```diff\n{diff}\n```'


def find_existing_comment(notes: list[ProjectMergeRequestNote], guard_str: str) -> ProjectMergeRequestNote | None:
    for note in notes:
        if guard_str in note.body:
            return note


def post_diff(diff_file: Path, mode: Literal['hr', 'ks'], mr: ProjectMergeRequest,
              notes: list[ProjectMergeRequestNote]):
    guard_str = f'<!-- flux-local diff {mode} -->'

    content = create_content(diff_file, mode, guard_str)
    comment = find_existing_comment(notes, guard_str)

    if comment is None:
        mr.notes.create({'body': content})
    else:
        comment.body = content
        comment.save()


def make_flux_comments():
    settings = Settings()

    logger.debug(settings)

    with gitlab.Gitlab(url=settings.gitlab.url,
                       private_token=settings.gitlab.private_token.get_secret_value()) as gl:
        # Fetch the user used.
        gl.auth()
        user = gl.user

        project = gl.projects.get(id=settings.project.project_id)
        mr = project.mergerequests.get(id=settings.project.merge_request_iid)

        # If the MR is not `opened`, no need to post comments
        if mr.state != 'opened':
            logger.error('MR state is not opened')
            exit(-1)

        # Fetch all notes owned by the user
        notes: list[ProjectMergeRequestNote] = []
        for note in mr.notes.list(iterator=True):
            if note.author['username'] != user.username:
                continue
            notes.append(note)

        logger.debug(notes)

        post_diff(Path('hr.diff'), mode='hr', mr=mr, notes=notes)
        post_diff(Path('ks.diff'), mode='ks', mr=mr, notes=notes)


if __name__ == '__main__':
    pass

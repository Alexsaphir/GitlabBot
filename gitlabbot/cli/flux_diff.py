import re
from pathlib import Path
from typing import Literal

import gitlab
from gitlab.v4.objects import ProjectMergeRequest, ProjectMergeRequestNote
from loguru import logger
from pydantic import Field
from pydantic_cli import Cmd, run_and_exit

from gitlabbot import Settings
from gitlabbot.note import find_note, make_note

type CommentMode = Literal['new', 'replace', 'recreate']
type FluxResource = Literal['hr', 'ks']
type DiffMode = Literal['diff', 'dyff']

flux_resources_name: dict[FluxResource, str] = {
        'hr': 'HelmRelease (Cluster side)',
        'ks': 'Kustomization (GitOps side)',
        }


def clean_diff(lines: list[str]) -> str:
    lines[1] = ''
    lines[3] = ''
    lines[5] = ''

    return ''.join(lines)


def clean_dyff(lines: list[str]) -> str:
    return re.sub(r'\n{3,}=(.*?)\n=(.*?)\n#(.*?)\n',
                  r'\n\n=\1\n=\2\n#\3\n',
                  ''.join(lines)).lstrip('\n').rstrip('\n')


def header_guard(flux_resource: FluxResource) -> str:
    return f'<!-- flux-local diff {flux_resource} -->'


def create_content(diff_file: Path,
                   flux_resource: FluxResource, diff_mode: DiffMode) -> str | None:
    with open(diff_file, 'r') as f:
        diff_lines = f.readlines()

    if not diff_lines:
        return None

    if diff_mode == 'diff':
        diff = clean_diff(diff_lines)
    elif diff_mode == 'dyff':
        diff = clean_dyff(diff_lines)
    else:
        raise ValueError(f'Unsupported diff mode: {diff_mode}')

    if diff == '':
        return None

    return f'{header_guard(flux_resource)}\n# {flux_resources_name[flux_resource]}\n```diff\n{diff}\n```'


def post_diff(diff_file: Path,
              flux_resource: FluxResource, diff_mode: DiffMode,
              comment_mode: CommentMode,
              mr: ProjectMergeRequest,
              notes: list[ProjectMergeRequestNote]):

    content = create_content(diff_file=diff_file,
                             flux_resource=flux_resource, diff_mode=diff_mode,
                             )

    notes = find_note(notes=notes, str_to_match=header_guard(flux_resource=flux_resource))

    make_note(resource=mr, note_content=content, existing_notes=notes, comment_mode=comment_mode)


class FluxDiffCommentArgs(Cmd):
    diff_file: Path
    flux_resource: FluxResource

    diff_mode: DiffMode = Field(default='diff')
    comment_mode: CommentMode = Field(default='recreate')

    def run(self) -> None:
        settings = Settings()

        logger.debug(f"Running with opts:{self}")
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

            post_diff(diff_file=self.diff_file,
                      comment_mode=self.comment_mode,
                      flux_resource=self.flux_resource, diff_mode=self.diff_mode,
                      mr=mr, notes=notes)


def flux_diff_comment():
    run_and_exit(FluxDiffCommentArgs, description="Post hr/ks diff comments.", version='0.2.6')

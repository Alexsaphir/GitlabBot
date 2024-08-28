from typing import Literal

from gitlab.v4.objects import (GroupEpic, GroupEpicNote, ProjectIssue, ProjectIssueNote, ProjectMergeRequest,
                               ProjectMergeRequestNote, ProjectSnippet,
                               ProjectSnippetNote, )
from loguru import logger

type CommentMode = Literal['new', 'replace', 'recreate']
type Resource = GroupEpic | ProjectMergeRequest | ProjectIssue | ProjectSnippet
type ResourceNote = GroupEpicNote | ProjectMergeRequestNote | ProjectIssueNote | ProjectSnippetNote


def find_note(notes: list[ResourceNote], str_to_match: str) -> list[ResourceNote] | None:
    return [note for note in notes if str_to_match in note.body]


def make_note(resource: Resource,
              note_content: str,
              comment_mode: CommentMode,
              existing_notes: list[ResourceNote]):
    comment_mode = comment_mode if len(existing_notes) > 0 else 'new'

    if comment_mode == 'recreate':
        for note in existing_notes:
            note.delete()

        comment_mode = 'new'

    if comment_mode == 'new':
        if note_content is None:
            logger.warning('No diff')
            return

        resource.notes.create({'body': note_content})
    elif comment_mode == 'replace':
        existing_notes[0].body = note_content
        existing_notes[0].save()
    else:
        raise ValueError

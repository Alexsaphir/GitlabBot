from typing import Literal

from gitlab.v4.objects import (GroupEpic, GroupEpicNote, ProjectIssue, ProjectIssueNote, ProjectMergeRequest,
                               ProjectMergeRequestNote, ProjectSnippet,
                               ProjectSnippetNote, )

type CommentMode = Literal['new', 'replace', 'recreate']
type Resource = GroupEpic | ProjectMergeRequest | ProjectIssue | ProjectSnippet
type ResourceNote = GroupEpicNote | ProjectMergeRequestNote | ProjectIssueNote | ProjectSnippetNote


def find_note(notes: list[ResourceNote], str_to_match: str) -> ResourceNote | None:
    for note in notes:
        if str_to_match in note.body:
            return note


def make_note(resource: Resource,
              note_content: str,
              comment_mode: CommentMode = 'new',
              existing_note: ResourceNote | None = None):
    comment_mode = comment_mode if existing_note is not None else 'new'

    if comment_mode == 'recreate':
        existing_note.delete()
        comment_mode = 'new'

    if comment_mode == 'new':
        resource.notes.create({'body': note_content})
    elif comment_mode == 'replace':
        existing_note.body = note_content
        existing_note.save()
    else:
        raise ValueError

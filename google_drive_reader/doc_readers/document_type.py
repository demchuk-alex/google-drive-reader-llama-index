class DocumentType:
    DOCUMENT = 'https://docs.google.com/document/d/'
    DOCX = 'https://docs.google.com/document/d/'
    SHEET = 'https://docs.google.com/spreadsheets/d/',
    PDF = 'https://drive.google.com/file/d/'


class ContentType:
    PARAGRAPH = 'paragraph'
    TABLE = 'table'
    TABLE_OF_CONTENTS = 'tableOfContents'


class DocumentMimeType:
    DOC = 'application/vnd.google-apps.document'
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    SHEET = 'application/vnd.google-apps.spreadsheet'
    PDF = 'application/pdf'

    @classmethod
    def as_list(cls):
        return [getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")]

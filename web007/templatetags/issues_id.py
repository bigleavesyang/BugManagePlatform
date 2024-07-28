from django.template import Library

register = Library()


@register.simple_tag
def change_issue_id(issue_id):
    if issue_id < 100:
        issue_id = str(issue_id).rjust(3, '0')
    return f'#{issue_id}'

from django.template import Library


register = Library()


@register.simple_tag
def user_space(size):
    if size > 1024*1024*1024:
        # .2f 保留两位小数
        return f'{size/(1024*1024*1024):.2f}G'
    elif size > 1024*1024:
        return f'{size/(1024*1024):.2f}M'
    elif size > 1024:
        return f'{size/1024:.2f}K'
    else:
        return f'{size}B'

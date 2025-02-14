import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BugManagePlatform.settings")
django.setup()


def run():
    from web007 import models

    models.ProjectStrategy.objects.create(
        project_type=1,
        project_title='VIP',
        project_price=100,
        project_count=50,
        project_max_collaborator=10,
        project_max_space=10,  # 10G
        project_max_file=500,  # 500M
    )

    models.ProjectStrategy.objects.create(
        project_type=1,
        project_title='SVIP',
        project_price=200,
        project_count=100,
        project_max_collaborator=100,
        project_max_space=20,  # 20G
        project_max_file=1000,  # 1000M
    )

    models.ProjectStrategy.objects.create(
        project_type=1,
        project_title='SSVIP',
        project_price=300,
        project_count=300,
        project_max_collaborator=300,
        project_max_space=40,  # 40G
        project_max_file=2000,  # 2000M
    )


if __name__ == '__main__':
    run()

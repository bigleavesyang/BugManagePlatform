import os
import sys
import django


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BugManagePlatform.settings')
django.setup()

from web007 import models

models.ProjectStrategy.objects.create(
    project_type=0,project_title='免费版',project_price=0,project_count=3,project_max_collaborator=2,
    project_max_space=50,project_max_file=5
)





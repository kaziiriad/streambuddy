from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time
import logging

class Command(BaseCommand):
    help = 'Cleanup temporary video files older than specified age'

    def add_arguments(self, parser):
        parser.add_argument(
            '--age',
            type=int,
            default=24,
            help='Age in hours after which to delete temporary files'
        )

    def handle(self, *args, **options):
        age_hours = options['age']
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        
        if not os.path.exists(temp_dir):
            self.stdout.write('No temp directory found')
            return

        now = time.time()
        count = 0

        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                filepath = os.path.join(root, name)
                if os.path.getmtime(filepath) < now - (age_hours * 3600):
                    try:
                        os.remove(filepath)
                        count += 1
                        self.stdout.write(f'Removed: {filepath}')
                    except Exception as e:
                        self.stderr.write(f'Failed to remove {filepath}: {e}')

            # Remove empty directories
            for name in dirs:
                dirpath = os.path.join(root, name)
                try:
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                        self.stdout.write(f'Removed empty directory: {dirpath}')
                except Exception as e:
                    self.stderr.write(f'Failed to remove directory {dirpath}: {e}')

        self.stdout.write(f'Successfully removed {count} temporary files')
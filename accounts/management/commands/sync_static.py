from django.core.management.base import BaseCommand
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Collect static files and sync with MinIO storage'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Collecting static files...')
            call_command('collectstatic', '--noinput')
            self.stdout.write(self.style.SUCCESS('Successfully collected and synced static files'))
        except Exception as e:
            logger.error(f'Error syncing static files: {str(e)}')
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 
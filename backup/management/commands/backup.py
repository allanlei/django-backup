from optparse import make_option
from subprocess import Popen, PIPE
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMessage

from socket import gethostname

class Command(BaseCommand):
    DEFAULT_SUBJECT = '%sDatabase Backup' % settings.EMAIL_SUBJECT_PREFIX
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database', default='default', help='Database to backup'),
        make_option('--filename', action='store', dest='filename', default=None, help='File location to write to'),
        make_option('--subject', action='store', dest='subject', default=DEFAULT_SUBJECT),
    )
    help = 'Send email backups of a database'

    def handle(self, *emails, **options):
        if len(emails) == 0:
            emails = [email for name, email in getattr(settings, 'DB_BACKUP_EMAILS', settings.ADMINS)]
        filename = options['filename'] or '/tmp/%s.backup' % settings.DATABASES[options['database']]['NAME']
        
        logger.info('Recipients: %s' % ', '.join(emails))
        if emails:
            self.backup(options['database'], filename)
            self.email(filename, emails=emails)
        else:
            logger.info('No emails to send backups to. Not creating backup.')
            
    def email(self, filename, emails=[], subject=DEFAULT_SUBJECT):
        logger.info('Sending to %s...' % ', '.join(emails))
        if emails:
            msg = EmailMessage(
                subject='%s (%s %s)' % (subject, gethostname(), settings.DEBUG and 'development' or 'production'),
                to = list(emails),
            )
            msg.attach_file(filename)
            msg.send()
        logger.info('\tDone')
        
    def backup(self, database, *args, **kwargs):
        logger.info('Backuping up "%s"...' % database)
        if settings.DATABASES[database]['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
            self.postgresql(database, *args, **kwargs)
        logger.info('\tOK')
            
    def postgresql(self, database, filename, cmd='/usr/bin/pg_dump', format='custom'):
        pf = Popen(
            [cmd,
                '--format', format,
                '--blobs',
                '--file', filename,
                '-U', settings.DATABASES[database]['USER'],
                settings.DATABASES[database]['NAME']
            ],
            env = {
                'PGPASSWORD': settings.DATABASES[database]['PASSWORD']
            },
            stdout=PIPE
        )
        return pf.communicate()[0]

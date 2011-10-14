from optparse import make_option
from subprocess import Popen, PIPE
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMessage
import sys

from socket import gethostname

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--database', choices=settings.DATABASES.keys(), default='default', help='Database to backup'),
        
        make_option('-o', '--output', choices=['file', 'stdout', 'email'], default='email', help='Output to file or stout or email'),
        make_option('-f', '--filename', default='database.backup', help='File location to write to if output is file'),
        
        make_option('-s', '--subject', default='%s Database Backup' % settings.EMAIL_SUBJECT_PREFIX),
    )
    help = 'Send email backups of a database'

    def handle(self, *emails, **options):
        self.filename = options['filename'] if options['output'] == 'file' else None
        self.file_content = None
        self.file_written = False
        
        self.backup(options['database'], filename=self.filename)
        
        if options['output'] == 'stdout':
            sys.stdout.write(self.file_content)
        elif options['output'] == 'email':
            if emails:
                self.email(*emails, subject=options['subject'], filename=options['filename'])
        elif options['output'] == 'file' and not self.file_written and self.file_content:
            print 'write file'
        

    def backup(self, database, *args, **kwargs):
        if settings.DATABASES[database]['ENGINE'] in ['django.db.backends.postgresql_psycopg2']:
            self.file_content = self.postgresql(database, *args, **kwargs)
        
    def postgresql(self, database, filename=None, cmd='pg_dump'):
        cmd_args = [
            '--format', 'custom',
            '--blobs',
            '-U', settings.DATABASES[database]['USER'],
        ]
        if filename:
            cmd_args.append('--file')
            cmd_args.append(filename)
            self.filename = filename
            self.file_written = True
        
        pf = Popen([cmd] + cmd_args + [settings.DATABASES[database]['NAME']], 
            env = {
                'PGPASSWORD': settings.DATABASES[database]['PASSWORD']
            },
            stdout=PIPE
        )
        return pf.communicate()[0]

    def email(self, *emails, **kwargs):
        msg = EmailMessage(
            subject=kwargs.get('subject', None),
            to = list(emails),
        )
        
        if self.filename:
            msg.attach_file(self.filename)
        elif self.file_content:
            msg.attach(kwargs.get('filename'), self.file_content)
        msg.send()

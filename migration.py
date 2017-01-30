from musicdb import MigrationManager, database
import sys

if __name__ == '__main__':
    manager = MigrationManager(database.Database("musicbot", '', 'musicbot'))

    # arguments parsing

    # first arguments is the job to execute

    args = sys.argv
    nb_args = len(args)
    job_name = None
    job_args = []

    for i in range(nb_args):
        if i == 0:
            continue

        if i == 1:
            job_name = args[i]
        else:
            job_args = args[i:]

    if job_name is None:
        print("Job not specified")
        sys.exit(-1)

    if job_name == 'new-migration' and len(job_args) >= 1:
        migration_name = job_args[0]
        manager.new_migration(migration_name)
        sys.exit(0)
    elif job_name == 'update-migration':
        manager.update_migration()
        sys.exit(0)
    elif job_name == 'revert' and len(job_args) >= 1:
        target = int(job_args[0])
        manager.revert_to(target)
        sys.exit(0)
    elif job_name == 'upgrade' and len(job_args) >= 1:
        target = int(job_args[0])
        manager.upgrade_to(target)
        sys.exit(0)

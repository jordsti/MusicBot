from ..migration import Migration


class %MIGRATION_NAME%(Migration):
    def __init__(self):
        Migration.__init__(self, '%MIGRATION_NAME%', %MIGRATION_NUMBER%)

    def up(self, connection):
        # fill this stub
        pass

    def down(self, connection):
        # fill this stub
        pass
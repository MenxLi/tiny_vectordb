from tiny_vectordb.diskio import SqliteIO
import os


if os.path.exists('test.db'):
    os.remove('test.db')
disk_io = SqliteIO('test.db')
disk_io.touchTable('test')
disk_io.insetToTable('test', '1', "hello")
disk_io.insetToTable('test', '2', "world")
disk_io.commit()
disk_io.insetToTable('test', 'xx', "!")
disk_io.deleteFromTable('test', '1')
disk_io.updateTable("test", '2', "world!")
print(disk_io.getTableNames())
print(disk_io.getTableData('test'))


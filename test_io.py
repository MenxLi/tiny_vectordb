from tiny_vectordb.diskio import SqliteIO


disk_io = SqliteIO('test.db')
disk_io.touchTable('test', 512)
disk_io.insetToTable('test', '1', [1.0] * 512)
disk_io.insetToTable('test', '2', [2.0] * 512)
disk_io.commit()
print(disk_io.getTableNames())


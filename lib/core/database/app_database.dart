import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

/// Owns the single SQLite connection used by the application.
///
/// Add the tables from the official assignment to [_onCreate]. Keeping the
/// connection here makes it easy to add repositories without coupling SQL to
/// widgets.
class AppDatabase {
  AppDatabase._();

  static final AppDatabase instance = AppDatabase._();

  static const String databaseName = 'midtern_project.db';
  static const int databaseVersion = 1;

  Database? _database;

  Future<Database> get database async {
    final currentDatabase = _database;
    if (currentDatabase != null) {
      return currentDatabase;
    }

    final databasePath = await getDatabasesPath();
    _database = await openDatabase(
      join(databasePath, databaseName),
      version: databaseVersion,
      onConfigure: (db) => db.execute('PRAGMA foreign_keys = ON'),
      onCreate: _onCreate,
    );
    return _database!;
  }

  Future<void> _onCreate(Database db, int version) async {
    // The CREATE TABLE statements will be added after the schema is announced.
  }

  Future<void> close() async {
    final currentDatabase = _database;
    if (currentDatabase == null) {
      return;
    }

    await currentDatabase.close();
    _database = null;
  }
}

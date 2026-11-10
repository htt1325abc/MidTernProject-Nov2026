import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

import '../firebase_options.dart';

abstract final class AppBootstrap {
  static const bool useFirebaseEmulator = bool.fromEnvironment(
    'USE_FIREBASE_EMULATOR',
    defaultValue: false,
  );

  static const String demoAdminEmail = 'admin@userhub.local';
  static const String demoAdminPassword = 'Admin@123';

  static Future<void> initialize() async {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );

    if (useFirebaseEmulator) {
      await FirebaseAuth.instance.useAuthEmulator('127.0.0.1', 9099);
      FirebaseDatabase.instance.useDatabaseEmulator('127.0.0.1', 9000);
      unawaited(_ensureDemoAdmin());
    }
  }

  static Future<void> _ensureDemoAdmin() async {
    try {
      await FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: demoAdminEmail,
        password: demoAdminPassword,
      );
    } on FirebaseAuthException catch (error) {
      if (error.code != 'email-already-in-use') {
        rethrow;
      }
    } finally {
      await FirebaseAuth.instance.signOut();
    }
  }
}

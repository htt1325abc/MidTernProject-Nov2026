import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';

/// Production Firebase configuration.
///
/// FlutterFire CLI replaces this file with the real Android and web options.
/// The placeholder keeps local emulator builds deterministic until the Firebase
/// account is connected.
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }

    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      default:
        throw UnsupportedError('Firebase is configured for Android and web.');
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyDtTimGE2j8qANVVXpFbI29cZi_WcJ9FdY',
    appId: '1:563256527342:web:65c73a4458d93fddb026ff',
    messagingSenderId: '563256527342',
    projectId: 'midtern-users-2026-htt1325',
    authDomain: 'midtern-users-2026-htt1325.firebaseapp.com',
    databaseURL: 'https://midtern-users-2026-htt1325-default-rtdb.asia-southeast1.firebasedatabase.app',
    storageBucket: 'midtern-users-2026-htt1325.firebasestorage.app',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyBRMXRZLk1Q0AXvXq9lEybh3nuhXVGlA2I',
    appId: '1:563256527342:android:1b920524d458f74fb026ff',
    messagingSenderId: '563256527342',
    projectId: 'midtern-users-2026-htt1325',
    databaseURL: 'https://midtern-users-2026-htt1325-default-rtdb.asia-southeast1.firebasedatabase.app',
    storageBucket: 'midtern-users-2026-htt1325.firebasestorage.app',
  );
}

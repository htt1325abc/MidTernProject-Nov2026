import 'package:flutter_test/flutter_test.dart';
import 'package:midtern_project/app/app.dart';

void main() {
  testWidgets('starter screen renders the project readiness state', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const App());

    expect(find.text('Project đã sẵn sàng'), findsOneWidget);
    expect(find.text('Flutter Android'), findsOneWidget);
    expect(find.text('SQLite'), findsOneWidget);
    expect(find.text('Cấu trúc sạch'), findsOneWidget);
  });
}

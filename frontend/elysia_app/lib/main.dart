import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  runApp(const ElysiaApp());
}

class ElysiaApp extends StatelessWidget {
  const ElysiaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Elysia',
      theme: ThemeData.dark(),
      home: const AskScreen(),
    );
  }
}

class AskScreen extends StatefulWidget {
  const AskScreen({super.key});

  @override
  State<AskScreen> createState() => _AskScreenState();
}

class _AskScreenState extends State<AskScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<String> _messages = [];
  WebSocketChannel? _channel;
  String? apiKey = dotenv.env['GROQ_API_KEY'];
  String _selectedProvider = "groq";
  final TextEditingController _systemController = TextEditingController(
    text: "You are a helpful AI assistant.",
  );
  @override
  void initState() {
    super.initState();
    _connectWebSocket();
  }

  void _connectWebSocket() {
    _channel = WebSocketChannel.connect(Uri.parse('ws://localhost:8080/ask'));
    _channel!.stream.listen(
      (message) {
        setState(() {
          _messages.add(message);
        });
      },
      onError: (error) {
        setState(() {
          _messages.add('Error: $error');
        });
      },
      onDone: () => _reconnect(),
    );
  }

  void _reconnect() {
    Future.delayed(const Duration(seconds: 1), _connectWebSocket);
  }

  void _sendPrompt() {
    if (_controller.text.isEmpty || _channel == null) return;

    final request = {
      'provider': _selectedProvider,
      'api_key': apiKey,
      'prompt': _controller.text,
      'system_prompt': _systemController.text,
    };
    _channel!.sink.add(jsonEncode(request));
    setState(() {
      _messages.add('You: ${_controller.text}');
      _controller.clear();
    });
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ask')),
      body: Column(
        children: [
          DropdownButton<String>(
            value: _selectedProvider,
            items: [
              'groq',
              'openai',
              'google',
              'ollama',
            ].map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
            onChanged: (value) => setState(() => _selectedProvider = value!),
          ),
          TextField(
            controller: _systemController,
            decoration: const InputDecoration(hintText: 'System Prompt'),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) =>
                  ListTile(title: Text(_messages[index])),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Ask something...',
                    ),
                    onSubmitted: (_) => _sendPrompt(),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _sendPrompt,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

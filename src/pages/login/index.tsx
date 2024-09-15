import { useEffect, useState } from "react";
import { Terminal } from 'lucide-react'

const bots = [
    { name: 'CodeGen Bot', id: 'codegen' },
    { name: 'Scheduler', id: 'scheduler' },
    { name: 'Task Manager', id: 'taskmanager' },
    { name: 'DocBot', id: 'docbot' },
  ]

export default function Main() {
    const [activeBot, setActiveBot] = useState<string | null>(null)
    const [messages, setMessages] = useState<string[]>([]);
    useEffect(() => {
        const socket = new WebSocket("ws://127.0.0.1:8000/ws");
  
        socket.addEventListener("open", () => {
          console.log("Connected to WebSocket");
        });
  
        socket.addEventListener("message", (event) => {
          console.log("Received message:", event.data);
          setMessages((prevMessages) => [...prevMessages, event.data]);
        });
  
        socket.addEventListener("close", () => {
          console.log("Disconnected from WebSocket");
        });
  
        return () => {
          socket.close();
        };
      }, []);

      return (
        <div className="flex flex-col h-screen bg-gray-100 w-full">
          <header className="bg-blue-600 text-white p-4 w-full text-center items-center justify-center">
            <h1 className="text-2xl font-bold text-center">Agent Modeling Dashboard</h1>
          </header>
          <div className="flex flex-1 overflow-hidden">
            <div className="w-1/3 p-4 bg-white shadow-md overflow-auto">
              <h2 className="text-xl font-semibold mb-4">Agents</h2>
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="text-left pb-2">Bot</th>
                    <th className="text-left pb-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {bots.map((bot) => (
                    <tr key={bot.id} className="border-t">
                      <td className="py-2">{bot.name}</td>
                      <td className="py-2">
                        <button
                          onClick={() => setActiveBot(activeBot === bot.id ? null : bot.id)}
                          className={`px-2 py-1 rounded ${
                            activeBot === bot.id
                              ? 'bg-green-500 text-white'
                              : 'bg-gray-200 text-gray-800'
                          }`}
                        >
                          {activeBot === bot.id ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex-1 p-4 overflow-hidden">
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg h-full font-mono overflow-auto">
                <div className="flex items-center mb-2 sticky">
                  <Terminal className="mr-2" />
                  <h3 className="text-xl font-semibold">Log Output</h3>
                </div>
                <div className="space-y-1">
                  {messages.length === 0 ? (
                    <div className="text-gray-500">No active bot. Logs will appear here when a bot is activated.</div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div key={idx}>{msg}</div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )
}
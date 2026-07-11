"use client";

import { useEffect, useRef, useState } from "react";
import { Plane, SendHorizonal } from "lucide-react";
import Message from "./Message";
import Typing from "./Typing";
import { sendMessage } from "../lib/api";

type MessageType = {
  role: "user" | "assistant";
  content: string;
  time: string;
};

export default function Chat() {
  const [messages, setMessages] = useState<MessageType[]>([]);

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          "👋 Welcome! I'm your AI Flight Booking Assistant.\n\nTell me where and when you'd like to travel.",
        time: new Date().toLocaleTimeString(),
      },
    ]);
  }, []);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  async function send() {
    if (!input.trim()) return;

    const user = {
      role: "user" as const,
      content: input,
      time: new Date().toLocaleTimeString(),
    };

    setMessages((m) => [...m, user]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage({
        message: input,
        thread_id: "default",
      });

      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            data.response ??
            data.message ??
            JSON.stringify(data, null, 2),
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Unable to reach server.",
          time: new Date().toLocaleTimeString(),
        },
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="flex h-screen">

      {/* Sidebar */}

      <aside className="hidden lg:flex w-72 border-r border-zinc-800 bg-[#0E0E10] flex-col">

        <div className="p-6 flex items-center gap-3 border-b border-zinc-800">

          <div className="rounded-xl bg-blue-600 p-3">
            <Plane />
          </div>

          <div>

            <h2 className="font-bold text-white">
              Flight AI
            </h2>

            <p className="text-xs text-zinc-400">
              Premium Booking Agent
            </p>

          </div>

        </div>

        <div className="p-6">

          <div className="rounded-xl bg-zinc-900 p-5">

            <h3 className="text-white mb-4">
              Capabilities
            </h3>

            <ul className="space-y-2 text-zinc-400 text-sm">

              <li>✓ Flight Search</li>
              <li>✓ Booking</li>
              <li>✓ Multi-city</li>
              <li>✓ Date Changes</li>
              <li>✓ Cheapest Fare</li>

            </ul>

          </div>

        </div>

      </aside>

      <section className="flex flex-1 flex-col">

        <header className="border-b border-zinc-800 p-5 bg-[#0F0F12]">

          <h1 className="text-xl font-bold text-white">
            AI Flight Booking Assistant
          </h1>

        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-8">

          {messages.map((m, i) => (
            <Message key={i} {...m} />
          ))}

          {loading && <Typing />}

          <div ref={bottomRef} />

        </div>

        <div className="border-t border-zinc-800 p-6">

          <div className="flex gap-4 rounded-2xl bg-zinc-900 p-3">

            <textarea
              rows={1}
              className="flex-1 resize-none bg-transparent outline-none text-white"
              value={input}
              placeholder="Ask about flights..."
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              onChange={(e) => setInput(e.target.value)}
            />

            <button
              onClick={send}
              className="rounded-xl bg-blue-600 px-5 hover:bg-blue-500 transition"
            >
              <SendHorizonal className="text-white"/>
            </button>

          </div>

        </div>

      </section>

    </div>
  );
}
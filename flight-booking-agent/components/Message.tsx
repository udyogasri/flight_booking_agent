import { Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function Message({
  role,
  content,
  time,
}: {
  role: "user" | "assistant";
  content: string;
  time: string;
}) {
  const ai = role === "assistant";

  return (
    <div
      className={`flex ${
        ai ? "" : "justify-end"
      }`}
    >
      <div
        className={`max-w-3xl rounded-3xl p-5 ${
          ai
            ? "bg-zinc-900"
            : "bg-blue-600"
        }`}
      >
        <div className="flex gap-3">

          {ai ? <Bot /> : <User />}

          <div>

            <div className="text-white">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed whitespace-pre-wrap">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-1">{children}</ol>,
                  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                  strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                }}
              >
                {content}
              </ReactMarkdown>
            </div>

            <div className="mt-3 text-xs text-zinc-400">
              {time}
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
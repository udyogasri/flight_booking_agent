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
                  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
                  h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2 text-white">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-lg font-bold mt-4 mb-2 text-white">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-md font-bold mt-3 mb-1 text-zinc-100">{children}</h3>,
                  code: ({ children }) => <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-sm font-mono text-zinc-200">{children}</code>,
                  table: ({ children }) => (
                    <div className="my-4 overflow-x-auto rounded-lg border border-zinc-800">
                      <table className="min-w-full divide-y divide-zinc-800 text-sm">
                        {children}
                      </table>
                    </div>
                  ),
                  thead: ({ children }) => <thead className="bg-zinc-800/40">{children}</thead>,
                  tbody: ({ children }) => <tbody className="divide-y divide-zinc-800/60 bg-zinc-950/10">{children}</tbody>,
                  tr: ({ children }) => <tr>{children}</tr>,
                  th: ({ children }) => (
                    <th className="px-4 py-2.5 text-left font-semibold text-zinc-200 border-b border-zinc-800">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="px-4 py-2.5 text-zinc-300">
                      {children}
                    </td>
                  ),
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
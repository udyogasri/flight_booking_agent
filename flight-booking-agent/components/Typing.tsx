export default function Typing() {
  return (
    <div className="flex gap-2 p-5 w-24 rounded-2xl bg-zinc-900">
      <div className="h-3 w-3 rounded-full bg-white animate-bounce"/>
      <div className="h-3 w-3 rounded-full bg-white animate-bounce delay-150"/>
      <div className="h-3 w-3 rounded-full bg-white animate-bounce delay-300"/>
    </div>
  );
}
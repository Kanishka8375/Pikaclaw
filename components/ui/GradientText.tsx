interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
}

export default function GradientText({
  children,
  className = "",
}: GradientTextProps) {
  return (
    <span
      className={`bg-gradient-to-r from-indigo-light via-pink to-pink-light bg-clip-text text-transparent ${className}`}
    >
      {children}
    </span>
  );
}

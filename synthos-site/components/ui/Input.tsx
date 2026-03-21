interface InputProps {
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  required?: boolean;
}

export default function Input({
  type = "text",
  placeholder,
  value,
  onChange,
  className = "",
  required = false,
}: InputProps) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      className={`
        w-full px-4 py-3 rounded-xl
        bg-void-light border border-void-border
        text-text-primary placeholder:text-text-muted
        focus:outline-none focus:border-indigo focus:ring-1 focus:ring-indigo/50
        transition-all duration-200
        ${className}
      `}
    />
  );
}

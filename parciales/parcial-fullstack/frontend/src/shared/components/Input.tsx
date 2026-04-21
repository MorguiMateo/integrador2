import type { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

interface InputFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function InputField({ label, error, id, ...rest }: InputFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-xs font-medium text-gray-600">
        {label}
      </label>
      <input
        id={id}
        {...rest}
        className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-gray-900"
      />
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </div>
  );
}

interface TextareaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
}

export function TextareaField({
  label,
  error,
  id,
  ...rest
}: TextareaFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-xs font-medium text-gray-600">
        {label}
      </label>
      <textarea
        id={id}
        {...rest}
        className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:border-gray-900"
      />
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </div>
  );
}

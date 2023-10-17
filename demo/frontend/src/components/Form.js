import { useState } from "react";
import { FaEye, FaEyeSlash } from "react-icons/fa";

import { Button } from "./Button";

function Textarea({ rounded, tight, ...props }) {
  return (
    <textarea
      {...props}
      className={`block h-full w-full grow bg-white text-sm text-gray-900 ${
        rounded ? "rounded-lg" : ""
      } ${
        tight ? "p-1" : "p-2.5"
      } resize-none border border-gray-300 focus:border-blue-500 focus:ring-blue-500`}
    />
  );
}

function PasswordToggle({ type, setType, small }) {
  let Icon;
  let nextType;
  if (type === "password") {
    Icon = FaEye;
    nextType = "text";
  } else {
    Icon = FaEyeSlash;
    nextType = "password";
  }
  return (
    <button type="button" onClick={() => setType(nextType)}>
      <Icon size={small ? 22 : 24} />
    </button>
  );
}

function Input({
  Icon,
  flatLeft,
  flatRight,
  small,
  right,
  bold,
  value,
  password,
  ...props
}) {
  let classExtra = "";

  if (small) classExtra += "p-1.5";
  else classExtra += "p-2.5";

  if (!flatLeft) classExtra += " rounded-l-lg";
  if (!flatRight) classExtra += " rounded-r-lg";
  if (right) classExtra += " text-right";
  if (Icon) {
    if (small) classExtra += " pl-9";
    else classExtra += " pl-10";
  }
  if (password) {
    if (small) classExtra += " pr-9";
    else classExtra += " pr-10";
  }
  if (bold) classExtra += " border-2 border-gray-600 ";
  else classExtra += " border border-gray-300 ";

  const [type, setType] = useState(password ? "password" : "text");

  return (
    <div className="relative h-full w-full">
      {Icon && (
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 flex items-center pl-3">
          <Icon size={small ? 18 : 22} className="text-gray-600" />
        </div>
      )}
      <input
        type={type}
        value={value ?? ""}
        {...props}
        className={`${classExtra} block h-full w-full min-w-0 bg-white text-sm text-gray-900 hover:outline hover:outline-1 hover:outline-blue-600 focus:z-10 focus:bg-blue-50 focus:outline focus:outline-1 focus:outline-blue-600`}
      />
      {password && (
        <div className="absolute inset-y-0 right-0 z-10 flex items-center pr-2">
          <PasswordToggle small={small} type={type} setType={setType} />
        </div>
      )}
    </div>
  );
}

function Checkbox({
  children,
  checked,
  onChange,
  onClickText,
  disabled,
  bold,
}) {
  const ChildComponent = onClickText ? (
    <Button appearance="link" onClick={onClickText}>
      {children}
    </Button>
  ) : (
    <span className={bold ? "text-sm font-bold" : null}>{children}</span>
  );
  const Inner = (
    <>
      <input
        type="checkbox"
        className="h-4 w-4 rounded border border-gray-300 bg-gray-50 focus:ring-1 focus:ring-blue-300"
        checked={!disabled && checked}
        onChange={onChange}
      />
      {ChildComponent}
    </>
  );
  const className =
    "inline-flex items-center justify-center whitespace-nowrap gap-2";
  if (onClickText) return <div className={className}>{Inner}</div>;
  return <label className={className}>{Inner}</label>;
}

export { Textarea, Input, Checkbox };

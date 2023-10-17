import React, { useRef, useState } from "react";
import { FaCheck, FaRegCopy, FaTrash } from "react-icons/fa";

import { Loading } from "./Loading";

const buttonStyles = {
  fill: {
    "*": "focus:outline-none transition text-white",
    primary:
      "bg-blue-600 hover:bg-blue-800 active:bg-blue-800 focus:ring-blue-300",
    secondary:
      "bg-gray-600 hover:bg-gray-800 active:bg-gray-800 focus:ring-gray-300",
    success:
      "bg-green-600 hover:bg-green-800 active:bg-green-800 focus:ring-green-300",
    warning:
      "bg-yellow-600 hover:bg-yellow-800 active:bg-yellow-800 focus:ring-yellow-300",
    danger: "bg-red-600 hover:bg-red-800 active:bg-red-800 focus:ring-red-300",
  },
  outline: {
    "*": "outline outline-1 focus:outline-none transition",
    primary:
      "text-blue-600 outline-blue-600 hover:text-white hover:bg-blue-600 active:bg-blue-800 focus:ring-blue-300",
    secondary:
      "text-gray-600 outline-gray-600 hover:text-white hover:bg-gray-600 active:bg-gray-800 focus:ring-gray-300",
    success:
      "text-green-600 outline-green-600 hover:text-white hover:bg-green-600 active:bg-green-800 focus:ring-green-300",
    warning:
      "text-yellow-600 outline-yellow-600 hover:text-white hover:bg-yellow-600 active:bg-yellow-800 focus:ring-yellow-300",
    danger:
      "text-red-600 outline-red-600 hover:text-white hover:bg-red-600 active:bg-red-800 focus:ring-red-300",
  },
  soft: {
    "*": "outline outline-1 shadow focus:outline-none transition",
    primary:
      "text-blue-600 bg-blue-50 outline-blue-200 hover:bg-blue-100 active:bg-blue-200 focus:ring-blue-300",
    secondary:
      "text-gray-600 bg-gray-50 outline-gray-300 hover:bg-gray-200 active:bg-gray-200 focus:ring-gray-300",
    success:
      "text-green-600 bg-green-50 outline-green-200 hover:bg-green-100 active:bg-green-200 focus:ring-green-300",
    warning:
      "text-yellow-600 bg-yellow-50 outline-yellow-200 hover:bg-yellow-100 active:bg-yellow-200 focus:ring-yellow-300",
    danger:
      "text-red-600 bg-red-50 outline-red-200 hover:bg-red-100 active:bg-red-200 focus:ring-red-300",
  },
  box: {
    "*": "border-b-2 focus:outline-none transition text-white",
    primary:
      "bg-blue-600 border-blue-900 hover:bg-blue-700 active:bg-blue-800 focus:ring-blue-300",
    secondary:
      "bg-gray-600 border-gray-900 hover:bg-gray-700 active:bg-gray-800 focus:ring-gray-300",
    success:
      "bg-green-600 border-green-900 hover:bg-green-700 active:bg-green-800 focus:ring-green-300",
    warning:
      "bg-yellow-600 border-yellow-900 hover:bg-yellow-700 active:bg-yellow-800 focus:ring-yellow-300",
    danger:
      "bg-red-600 border-red-900 hover:bg-red-700 active:bg-red-800 focus:ring-red-300",
  },
  link: {
    "*": "underline decoration-transparent hover:decoration-inherit transition duration-300 ease-in-out",
    primary: "text-blue-600 hover:text-blue-800",
    secondary: "text-gray-600 hover:text-gray-800",
    success: "text-green-600 hover:text-green-800",
    warning: "text-red-600 hover:text-red-800",
    danger: "text-yellow-600 hover:text-yellow-800",
  },
  softLink: {
    "*": "underline decoration-transparent hover:decoration-inherit transition duration-300 ease-in-out",
    primary: "text-blue-300 hover:text-blue-500",
    secondary: "text-gray-300 hover:text-gray-500",
    success: "text-green-300 hover:text-green-500",
    warning: "text-red-300 hover:text-red-500",
    danger: "text-yellow-300 hover:text-yellow-500",
  },
  disabled: {
    "*": "cursor-default text-sm text-white",
    primary: "bg-blue-300",
    secondary: "bg-gray-300",
    success: "bg-green-300",
    warning: "bg-yellow-300",
    danger: "bg-red-300",
  },
};

function Button({
  appearance = "fill",
  variant = "primary",
  href,
  small,
  disabled,
  children,
  flatRight,
  flatLeft,
  loading,
  wrap,
  ...props
}) {
  const a = disabled ? "disabled" : appearance;
  const isLink = ["link", "softLink"].indexOf(appearance) >= 0;

  let className = "font-bold tracking-tight focus:z-10";

  if (!wrap) className += " whitespace-nowrap";

  if (!isLink) className += " rounded-md";
  className += ` ${buttonStyles[a]["*"]}`;
  className += ` ${buttonStyles[a][variant]}`;

  if (flatRight) className += " rounded-r-[0]";
  if (flatLeft) className += " rounded-l-[0]";

  if (!isLink) {
    className += " text-sm"
    if (small) className += " px-2 py-[1px]";
    else className += " px-4 py-2";
  }
  if (!loading && !isLink && appearance !== "disabled")
    className += " focus:ring-2";

  const passProps = { ...props, className, disabled: a === "disabled" };

  let components = children;
  if (loading) {
    let loadingVariant = variant;
    if (appearance === "fill" || appearance === "box") loadingVariant = "white";
    components = (
      <div className="flex items-center gap-2">
        <Loading variant={loadingVariant} small />
        {children}
      </div>
    );
  }

  if (href)
    return (
      <a href={href} {...passProps}>
        {components}
      </a>
    );
  return (
    <button type="button" {...passProps}>
      {components}
    </button>
  );
}

function DeleteButton(props) {
  return (
    <Button {...props} appearence="box" variant="danger">
      <FaTrash size={16} className="p-[1px]" />
    </Button>
  );
}

function LoadingButton({ text, ...props }) {
  return (
    <Button {...props} loading>
      {typeof text === "string" ? text : "Loading"}...
    </Button>
  );
}

function CopyToClipboardButton({ text }) {
  const [saved, setSaved] = useState(false);
  const timeout = useRef();
  const onClick = () => {
    navigator.clipboard.writeText(text);
    setSaved(true);
    clearTimeout(timeout.current);
    timeout.current = setTimeout(() => setSaved(false), 1000);
  };
  if (saved)
    return (
      <Button variant="success">
        <FaCheck />
      </Button>
    );
  return (
    <Button appearance="fill" variant="primary" onClick={onClick}>
      <FaRegCopy />
    </Button>
  );
}

export { Button, DeleteButton, LoadingButton, CopyToClipboardButton };

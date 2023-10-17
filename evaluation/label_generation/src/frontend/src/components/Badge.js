const badgeStyles = {
  primary: "bg-blue-300 text-black",
  secondary: "bg-gray-300 text-black",
  success: "bg-green-300 text-black",
  warning: "bg-orange-300 text-black",
  danger: "bg-red-300 text-black",
};

const Badge = ({ children, variant = "primary", uppercase }) => (
  <span
    className={`${uppercase ? "uppercase" : ""} ${
      badgeStyles[variant]
    } p-[7px] whitespace-nowrap inline-flex items-center gap-2 leading-none align-baseline text-xs font-bold rounded-sm`}
  >
    {children}
  </span>
);

const BadgeGroup = ({ children }) => (
  <div className="flex flex-wrap gap-2">{children}</div>
);

export { Badge, BadgeGroup };

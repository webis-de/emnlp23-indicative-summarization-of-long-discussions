import React from "react";

function Card({ children, full }) {
  return (
    <div
      className={`${
        full ? "w-full" : "max-w-sm"
      } flex grow flex-col divide-y divide-slate-300 rounded-lg border border-gray-200 bg-slate-100 shadow-md`}
    >
      {children}
    </div>
  );
}

function CardHead({ children, tight }) {
  return (
    <div
      className={`${
        tight ? "min-h-[50px]" : "min-h-[80px] py-4"
      } flex w-full items-center justify-between gap-4 px-6`}
    >
      {children}
    </div>
  );
}

function CardContent({ children, white, tight }) {
  return (
    <div
      className={`${tight ? "p-3" : "p-6"} grow flex flex-col justify-between space-y-3 ${
        white ? "bg-white" : ""
      }`}
    >
      {children}
    </div>
  );
}

function CardFoot({ children }) {
  return <div className="p-6">{children}</div>;
}

export { Card, CardHead, CardContent, CardFoot };

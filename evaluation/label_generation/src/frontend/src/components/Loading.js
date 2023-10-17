import React from "react";

import { Spinner } from "./Spinner";

const Loading = ({ small, big, ...props }) => {
  let className = "w-[20px]"
  if (small) className="w-[15px]"
  else if (big) className="w-[50px]"
  return (
    <div className={className}>
      <Spinner {...props} />
    </div>
  );
};

const CenterLoading = (props) => (
  <div className="flex justify-center">
    <Loading {...props} />
  </div>
);

export { Loading, CenterLoading };

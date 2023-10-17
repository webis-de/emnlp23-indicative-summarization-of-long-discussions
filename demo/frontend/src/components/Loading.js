import { Middle } from "./Middle";
import { Spinner } from "./Spinner";

function Loading({ small, big, ...props }) {
  let className = "w-[20px]";
  if (small) className = "w-[15px]";
  else if (big) className = "w-[60px]";
  return (
    <div className={className}>
      <Spinner {...props} />
    </div>
  );
}

function CenterLoading({ message }) {
  return (
    <Middle>
      <div className="flex w-[90%] flex-col items-center gap-4 pb-[10%]">
        <Loading big />
        {message && (
          <div className="rounded-lg border-2 border-gray-500 bg-gray-200 px-1 py-[1px] text-sm opacity-80">
            {message}
          </div>
        )}
      </div>
    </Middle>
  );
}

export { Loading, CenterLoading };

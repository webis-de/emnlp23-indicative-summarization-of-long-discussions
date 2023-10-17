import { useNavigate } from "react-router-dom";

import { HTTPError } from "../request";
import { Middle } from "./Middle";

function ErrorWrapper({ children, head, retry }) {
  return (
    <Middle>
      <div className="flex w-[90%] max-w-[700px] flex-col items-center pb-[10%]">
        <div className="m-4 flex w-full flex-col items-center gap-4 break-all">
          <div className="w-full divide-y-2 divide-gray-800 overflow-hidden rounded-[15px] border-4 border-gray-600">
            {head && (
              <div className="bg-gray-500 px-3 py-[3px] text-white">{head}</div>
            )}
            <div className="bg-red-300 py-2 px-3">{children}</div>
          </div>
          {retry && (
            <button
              type="button"
              onClick={retry}
              className="rounded-lg border-2 border-gray-600 bg-blue-500 px-4 py-2 text-white hover:bg-blue-700"
            >
              Go Back
            </button>
          )}
        </div>
      </div>
    </Middle>
  );
}

function GeneralError({ error, retryPath }) {
  const navigate = useNavigate();
  const retry =
    retryPath &&
    (() => {
      navigate(retryPath);
    });
  if (error instanceof HTTPError) {
    const { code, detail } = error;
    return (
      <ErrorWrapper head={code} retry={retry}>
        {detail}
      </ErrorWrapper>
    );
  }
  const { message } = error;
  return <ErrorWrapper retry={retry}>{message}</ErrorWrapper>;
}

function ValidationError({ errors, retry }) {
  return (
    <ErrorWrapper
      head="The backend returned errors while validating the request"
      retry={retry}
    >
      <ul className="flex flex-col gap-2">
        {errors.map(({ loc, msg }, i) => (
          <li key={i} className="flex items-start gap-2">
            <div>
              <div className="flex gap-2 rounded-md bg-slate-200 p-[3px] pb-0 font-mono ring-2 ring-gray-400">
                {loc.map((e, j) => (
                  <span key={j}>{e}</span>
                ))}
              </div>
            </div>
            <span>{msg}</span>
          </li>
        ))}
      </ul>
    </ErrorWrapper>
  );
}

function SuccessFalseError({ error, message, errors, retryPath }) {
  const navigate = useNavigate();
  const retry =
    retryPath &&
    (() => {
      navigate(retryPath);
    });
  if (error === "VALIDATION") {
    return <ValidationError errors={errors} retry={retry} />;
  }
  return (
    <ErrorWrapper head="The backend returned errors" retry={retry}>
      {message}
    </ErrorWrapper>
  );
}

export { GeneralError, SuccessFalseError };

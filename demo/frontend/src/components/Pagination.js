import React, { useCallback, useState } from "react";

import { Categories } from "./Categories";

const parseNumber = (number) => {
  let cleanNumber = number;
  if (typeof number === "string") cleanNumber = number.replace(/\D/g, "");
  return cleanNumber ? parseInt(cleanNumber, 10) : null;
};

function InputField({ value: initValue, onDone }) {
  const [value, setValue] = useState(initValue);
  const accept = () => {
    let number = parseNumber(value);
    number = number != null ? number : initValue;
    setValue(initValue);
    onDone(number);
  };

  const onChange = (e) => {
    setValue(e.currentTarget.value);
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") {
      accept();
    }
  };

  return (
    <input
      type="text"
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      onBlur={accept}
      className="block w-12 min-w-0 border-2 border-slate-300 bg-white px-1.5 py-[2px] text-right text-sm text-gray-900 focus:z-10 focus:bg-blue-50 focus:outline focus:outline-2 focus:outline-blue-600"
    />
  );
}

function Label({ children }) {
  return (
    <span className="inline-flex items-center whitespace-nowrap bg-slate-300 px-2 text-sm text-gray-900 outline-gray-300">
      {children}
    </span>
  );
}

function Button({ isLeft, isRight, disabled, onClick, children }) {
  let className =
    "px-2 text-white font-bold text-sm disabled:bg-blue-200 disabled:cursor-default disabled:outline-blue-200 focus:z-10 leading-tight bg-blue-500 hover:bg-blue-700 active:bg-blue-800";
  if (isLeft) className += " rounded-l-md";
  if (isRight) className += " rounded-r-md";

  return (
    <button
      type="button"
      className={className}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

const SIZES = [5, 10, 25, 50, 100];
const SIZE_LABELS = SIZES.map((label) => ({ label }));

function Pagination({ numPages, page, setPage, size, setSize }) {
  return (
    <div className="flex items-center gap-2">
      <div className="inline-flex">
        <Button
          isLeft
          disabled={page <= 1}
          onClick={() => setPage((old) => old - 1)}
        >
          Previous
        </Button>
        <InputField key={page} value={page} onDone={setPage} />
        <Label>
          /&nbsp;<span className="font-bold">{numPages}</span>
        </Label>
        <Button
          isRight
          disabled={page >= numPages}
          onClick={() => setPage((old) => old + 1)}
        >
          Next
        </Button>
      </div>
      {size !== undefined && (
        <div className="">
          <Categories
            index={SIZES.indexOf(size)}
            onChange={(index) => {
              setSize(SIZES[index]);
            }}
            notNullable
            categories={SIZE_LABELS}
          />
        </div>
      )}
    </div>
  );
}

const clip = (value, minValue, maxValue) => {
  let _value = value;
  if (Number.isInteger(maxValue)) _value = Math.min(maxValue, _value);
  if (Number.isInteger(minValue)) _value = Math.max(minValue, _value);
  return _value;
};

function validateNumber(newNumber, oldNumber, minNumber, maxNumber) {
  let tmp = typeof newNumber === "function" ? newNumber(oldNumber) : newNumber;
  tmp = parseNumber(tmp);
  tmp = typeof tmp === "number" && Number.isFinite(tmp) ? tmp : oldNumber;
  tmp = clip(tmp, minNumber, maxNumber);
  return tmp;
}

const usePagination = (
  numItems,
  { maxSize, initialPage = 1, initialSize = 10 }
) => {
  const updateState = useCallback(
    ({ newSize, newPage, oldSize, oldPage }) => {
      const _nextSize = validateNumber(newSize, oldSize, 1, maxSize);
      const _numPages = Math.max(Math.ceil(numItems / _nextSize), 1);
      let _nextPage =
        newPage === undefined &&
        oldPage !== undefined &&
        newSize !== undefined &&
        oldSize !== undefined
          ? Math.ceil((oldSize * (oldPage - 1) + 1) / _nextSize)
          : newPage;
      _nextPage = validateNumber(_nextPage, oldPage, 1, _numPages);
      return {
        size: _nextSize,
        page: _nextPage,
        numPages: _numPages,
        numItems,
      };
    },
    [numItems, maxSize]
  );

  const init = useCallback(
    () => updateState({ newSize: initialSize, newPage: initialPage }),
    [updateState, initialSize, initialPage]
  );

  const [{ size, page, numPages, numItems: currentNumItems }, _setParams] =
    useState(init);

  const reset = useCallback(() => _setParams(init()), [init]);

  const setParams = useCallback(
    ({ size: newSize, page: newPage }) => {
      _setParams(({ size: oldSize, page: oldPage }) =>
        updateState({ newSize, newPage, oldSize, oldPage })
      );
    },
    [updateState]
  );
  const setPage = useCallback(
    (newPage) => {
      setParams({ page: newPage });
    },
    [setParams]
  );
  const setSize = useCallback(
    (newSize) => {
      setParams({ size: newSize });
    },
    [setParams]
  );

  if (numItems !== currentNumItems) {
    reset();
  }

  return { page, numPages, setPage, size, setSize, reset };
};

export { Pagination, usePagination };

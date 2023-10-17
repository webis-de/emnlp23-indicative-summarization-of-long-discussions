import React, { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Select from "react-select";

import { toTitlecase } from "../util/common";
import { Button } from "./Button";

function LabelText({ color, children }) {
  return (
    <div className="flex gap-2">
      {color && (
        <div>
          <div
            className="mt-[6px] rounded-full border-black p-[8px] outline outline-2 outline-slate-700"
            style={{ backgroundColor: color }}
          />
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}

function Option({ value, label }) {
  if (value === -1) {
    return <div className="text-[#8082a1]">{label}</div>;
  }
  if (typeof label === "string") return <div>{label}</div>;
  return <LabelText color={label.color}>{label.label}</LabelText>;
}

function Categories({
  onChange,
  index,
  categories,
  notNullable,
  nullValue = "-- select a value --",
}) {
  const options = categories.map((category, i) => ({
    value: i,
    isFirst: false,
    label: category,
  }));
  const nullOption = { value: -1, isFirst: false, label: nullValue };
  const allOptions = [...options];
  if (!notNullable) allOptions.splice(0, 0, nullOption);
  if (allOptions.length) allOptions[0].isFirst = true;
  return (
    <Select
      placeholder={nullValue}
      formatOptionLabel={Option}
      isSearchable={false}
      styles={{
        option: (styles, { data: { value, isFirst } }) => {
          const newStyles = {
            ...styles,
            padding: "3px 10px",
            whiteSpace: "pre-line",
          };
          if (value === -1) newStyles.color = "#8082a1";
          if (!isFirst) {
            newStyles.borderTopWidth = "1px";
            newStyles.borderColor = "#999999";
          }
          return newStyles;
        },
      }}
      value={Number.isInteger(index) && index >= 0 ? options[index] : null}
      onChange={({ value }) => onChange(value)}
      options={allOptions}
    />
  );
}

const commonClassName = "text-left px-2 py-1";
const selectedClassName = `${commonClassName} bg-blue-500 text-white`;
const unSelectedClassName = `${commonClassName} hover:bg-blue-100`;

function AltOption({
  parentRef,
  isSelected,
  link,
  onChange,
  value,
  scrollKey,
  ...props
}) {
  const ref = useRef();
  useEffect(() => {
    if (parentRef && isSelected) {
      const parentHeight = parentRef.current.offsetHeight;
      const thisHeight = ref.current.offsetHeight;
      parentRef.current.scroll({
        top: ref.current.offsetTop - parentHeight / 2 + thisHeight / 2,
        left: 0,
      });
    }
  }, [isSelected, parentRef, scrollKey]);

  let element = <Option value={value} {...props} />;
  if (onChange) {
    element = (
      <button
        ref={ref}
        className={isSelected ? selectedClassName : unSelectedClassName}
        type="button"
        onClick={() => onChange(value)}
      >
        {element}
      </button>
    );
  } else {
    element = (
      <Link ref={ref} to={link} className={unSelectedClassName}>
        {element}
      </Link>
    );
  }
  return element;
}

function AltCategories({
  onChange,
  makeHref,
  index,
  categories,
  parentRef,
  scrollKey,
  notNullable,
  nullValue = "-- unselect --",
}) {
  const selectedIndex = Number.isInteger(index) && index >= 0 ? index : -1;
  const options = categories.map((category, i) => ({
    value: i,
    label: category,
  }));
  const nullOption = { value: -1, label: nullValue };
  const allOptions = [...options];
  if (!notNullable) allOptions.splice(0, 0, nullOption);
  return (
    <div className="flex w-full flex-col divide-y divide-gray-300">
      {allOptions.map(({ value, ...props }) => (
        <AltOption
          key={value}
          parentRef={parentRef}
          isSelected={value !== -1 && value === selectedIndex}
          link={makeHref && makeHref(value)}
          onChange={onChange}
          scrollKey={scrollKey}
          value={value}
          {...props}
        />
      ))}
    </div>
  );
}

function TreeCategories({
  onChange,
  makeFrameHref,
  makeHref,
  onRootClick,
  index,
  categories,
  scrollKey,
  parentRef,
}) {
  const selectedIndex = Number.isInteger(index) && index >= 0 ? index : -1;
  let i = -1;
  const options = categories.map(([root, children]) => [
    root,
    children.map((category) => {
      i += 1;
      return {
        value: i,
        label: category,
      };
    }),
  ]);
  return (
    <div className="w-full pl-1">
      {options.map(([rootName, children]) => {
        let root = toTitlecase(rootName);
        if (makeFrameHref) {
          root = (
            <Link to={makeFrameHref(rootName)} className={unSelectedClassName}>
              {root}
            </Link>
          );
        } else if (onRootClick) {
          root = <Button appearance="link" onClick={() => onRootClick(rootName)}>{root}</Button>;
        } else {
          root = <div className="text-left">{root}</div>;
        }
        return (
          <div key={rootName}>
            <div className="font-bold">{root}</div>
            <div className="flex">
              <div className="my-1 ml-1 mr-1 border-l-2 border-b-2 border-black px-1" />
              <div className="flex grow flex-col divide-y divide-gray-300 ">
                {children.map(({ value, ...props }) => (
                  <AltOption
                    key={value}
                    parentRef={parentRef}
                    isSelected={value === selectedIndex}
                    onChange={onChange}
                    link={makeHref && makeHref(value)}
                    scrollKey={scrollKey}
                    value={value}
                    {...props}
                  />
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export { Categories, LabelText, AltCategories, TreeCategories };

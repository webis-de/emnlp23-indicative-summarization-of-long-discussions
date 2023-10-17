import React, { useState, useCallback, useEffect, useRef } from "react";
import { Button } from "./components/Button";
import { Badge } from "./components/Badge";
import { useAsync, useKey } from "react-use";
import { getExamples, updateRanking } from "./api";
import { Loading } from "./components/Loading";
import { Modal, ModalTitle, useModal } from "./components/Modal";
import {
  useParams,
  BrowserRouter,
  useRoutes,
  Link,
  useNavigate,
} from "react-router-dom";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

const omap = (obj, func, kind = "value") => {
  switch (kind) {
    case "value":
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => [key, func(value, key)])
      );
    case "full":
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => func(key, value))
      );
    case "key":
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => [func(key, value), value])
      );
    default:
      throw new Error(`unknown kind ${kind}`);
  }
};

function shuffle(array) {
  return array
    .map((value) => ({ value, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ value }) => value);
}

const colors = [
  "#bbffff",
  "#ffddff",
  "#ffffcc",
  "#ddddff",
  "#ffdddd",
  "#ddffdd",
];

function DragElement({ children, id, index, rank, colorIndex }) {
  return (
    <Draggable draggableId={id} index={index}>
      {({ draggableProps, dragHandleProps, innerRef }) => (
        <div
          ref={innerRef}
          {...draggableProps}
          {...dragHandleProps}
          className="mb-6"
        >
          <div
            className="border border-black rounded p-1"
            style={{
              overflowWrap: "break-word",
              wordBreak: "all",
              backgroundColor: colors[colorIndex % colors.length],
            }}
          >
            <span className="font-bold w-7 inline-block">
              {rank === undefined ? "•" : rank}
            </span>
            <span>{children}</span>
          </div>
        </div>
      )}
    </Draggable>
  );
}

const Unranked = React.memo(
  ({ unranked, example: { hypotheses, colorIndexes } }) =>
    unranked.map((key, i) => (
      <DragElement key={key} id={key} index={i} colorIndex={colorIndexes[key]}>
        {hypotheses[key]}
      </DragElement>
    ))
);

const Ranking = React.memo(
  ({ ranking, example: { hypotheses, colorIndexes } }) =>
    ranking.map((key, i) => (
      <DragElement
        key={key}
        id={key}
        index={i}
        rank={i + 1}
        colorIndex={colorIndexes[key]}
      >
        {hypotheses[key]}
      </DragElement>
    ))
);

function ExampleInner({ unranked, ranking, modifyRanking, example }) {
  function onDragEnd({ draggableId: element, source, destination }) {
    if (
      !destination ||
      (destination.droppableId === source.droppableId &&
        destination.index === source.index)
    )
      return;
    modifyRanking({
      source: { id: source.droppableId, index: source.index },
      destination: { id: destination.droppableId, index: destination.index },
      element,
    });
  }
  return (
    <div className="overflow-hidden h-full p-3">
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-2 gap-4 h-full overflow-hidden">
          <div className="w-full flex flex-col overflow-hidden">
            <Droppable droppableId="unranked">
              {({ droppableProps, innerRef, placeholder }) => (
                <div
                  className="p-2 pb-0 grow overflow-y-auto overflow-x-hidden"
                  ref={innerRef}
                  {...droppableProps}
                >
                  <div className="grow">
                    <Unranked unranked={unranked} example={example} />
                    {placeholder}
                  </div>
                </div>
              )}
            </Droppable>
          </div>
          <div className="w-full flex flex-col overflow-hidden">
            <Droppable droppableId="ranking">
              {({ droppableProps, innerRef, placeholder }) => (
                <div
                  className="p-2 pb-0 grow overflow-y-auto overflow-x-hidden border-4 border-orange-300"
                  ref={innerRef}
                  {...droppableProps}
                >
                  <Ranking ranking={ranking} example={example} />
                  {placeholder}
                </div>
              )}
            </Droppable>
          </div>
        </div>
      </DragDropContext>
    </div>
  );
}

function Example({ entry, modifyRanking }) {
  const { example, unranked, ranking } = entry;
  const { reference, title, top_sentences, random_sentences } = example;
  const [sentenceModalIsOpen, openSentenceModal, closeSentenceModal] =
    useModal();
  return (
    <div className="flex flex-col min-w-0 overflow-hidden h-full">
      <div className="flex flex-col grow overflow-hidden">
        <div className="bg-blue-100 text-blue-700 px-2 py-4">
          <span className="font-bold mr-4">Title</span>
          <span className="text-xl">{title}</span>
        </div>
        <div className="bg-gray-100 flex items-center gap-2 justify-between px-2 py-4">
          <div className="text-gray-700">
            <span className="font-bold mr-4">Reference</span>
            <span className="text-xl">{reference}</span>
          </div>
          <div>
            <Button onClick={openSentenceModal}>show cluster</Button>
            <Modal isOpen={sentenceModalIsOpen} close={closeSentenceModal}>
              <div className="bg-slate-100 p-5 sticky z-20 top-0 flex flex-wrap justify-between items-center border-b">
                <ModalTitle>Cluster</ModalTitle>
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    appearance="soft"
                    variant="primary"
                    onClick={closeSentenceModal}
                  >
                    Close
                  </Button>
                </div>
              </div>
              <div className="px-4 py-2">
                <div className="font-bold text-lg">
                  Central Sentences from Cluster
                </div>
                <div className="flex flex-col py-2 px-5 [&>*:not(:first-child)]:pt-1 [&>*:not(:last-child)]:pb-1 divide-y">
                  {top_sentences.map((sentence) => (
                    <div>{sentence}</div>
                  ))}
                </div>
                <div className="font-bold text-lg mt-4">
                  Random Sentences from Cluster
                </div>
                <div className="flex flex-col py-2 px-5 [&>*:not(:first-child)]:pt-1 [&>*:not(:last-child)]:pb-1 divide-y">
                  {random_sentences.map((sentence) => (
                    <div>{sentence}</div>
                  ))}
                </div>
              </div>
            </Modal>
          </div>
        </div>
        <ExampleInner
          unranked={unranked}
          ranking={ranking}
          modifyRanking={modifyRanking}
          example={example}
        />
      </div>
    </div>
  );
}

function ExampleCard({ isSelected, id, index, reference, unranked, ranking }) {
  const numDone = ranking.length;
  const numTotal = unranked.length + ranking.length;
  let background;
  if (isSelected) background = "bg-gray-600 text-gray-200";
  else if (numDone === numTotal) background = "bg-green-300 hover:bg-green-400";
  else if (numDone > 0) background = "bg-orange-300 hover:bg-orange-400";
  else background = "bg-gray-300 hover:bg-gray-400";
  return (
    <div className={`overflow-hidden py-1 px-2 ${background}`}>
      <div className="flex justify-between">
        <div className="flex items-end gap-2">
          <div className="font-bold">{index}</div>
          <div className="text-sm">{id}</div>
        </div>
        <div>
          {numDone}/{numTotal}
        </div>
      </div>
      <div className="whitespace-nowrap overflow-hidden text-ellipsis">
        {reference}
      </div>
    </div>
  );
}

function ExampleList({ initialRankings, userId, selectedExampleId }) {
  const [rankings, setRanking] = useState(initialRankings);
  const [orderedRankingKeys] = useState(() =>
    Object.keys(rankings).sort((key1, key2) =>
      key1 < key2 ? -1 : key1 > key2 ? 1 : 0
    )
  );
  const parentRef = useRef();
  const childRef = useRef();
  const scrollRef = useRef();
  useEffect(() => {
    if (parentRef.current && childRef.current) {
      const parentHeight = parentRef.current.offsetHeight;
      const childHeight = childRef.current.offsetHeight;
      clearTimeout(scrollRef.current);
      scrollRef.current = setTimeout(() => {
        if (parentRef.current)
          parentRef.current.scroll({
            top:
              childRef.current.offsetTop - parentHeight / 2 + childHeight / 2,
            left: 0,
            behavior: "smooth",
          });
      }, 100);
    }
  }, [selectedExampleId]);
  const [error, setError] = useState(null);
  const modifyRanking = useCallback(
    ([exampleId, { source, destination, element }]) => {
      setRanking((state) => {
        const entry = state[exampleId];
        const previous_unranked = [...entry.unranked];
        const previous_ranking = [...entry.ranking];
        entry.unranked = [...entry.unranked];
        entry.ranking = [...entry.ranking];
        entry[source.id].splice(source.index, 1);
        entry[destination.id].splice(destination.index, 0, element);
        const next_unranked = [...entry.unranked];
        const next_ranking = [...entry.ranking];
        updateRanking(userId, exampleId, {
          previous_unranked: previous_unranked,
          previous_ranking: previous_ranking,
          next_unranked: next_unranked,
          next_ranking: next_ranking,
        })
          .then(({ success, reason }) => {
            if (!success) setError(reason);
          })
          .catch((e) => {
            setError(e.message);
          });
        return { ...state, [exampleId]: { ...entry } };
      });
    },
    [userId, setRanking]
  );
  const selectedIndex = useRef(-1);
  selectedIndex.current = orderedRankingKeys.findIndex(
    (thisExampleId) => thisExampleId === selectedExampleId
  );
  const navigate = useNavigate();
  const select = useCallback(
    (index) => {
      if (index < 0 || index >= orderedRankingKeys.length) return;
      const exampleId = orderedRankingKeys[index];
      navigate(`/${userId}/${exampleId}`);
    },
    [navigate, orderedRankingKeys, userId]
  );
  useEffect(() => {
    if (selectedExampleId === undefined && orderedRankingKeys.length > 0) {
      let nextIndex = orderedRankingKeys.findIndex(
        (thisExampleId) => rankings[thisExampleId].unranked.length !== 0
      );
      if (nextIndex === -1) nextIndex = 0;
      select(nextIndex);
    }
  }, [orderedRankingKeys, rankings, select, selectedExampleId]);
  const selectRelative = (offset) => {
    if (selectedIndex.current === -1) return;
    select(selectedIndex.current + offset);
  };
  const nextExample = () => selectRelative(1);
  const previousExample = () => selectRelative(-1);
  useKey("ArrowRight", nextExample);
  useKey("ArrowDown", nextExample);
  useKey("ArrowUp", previousExample);
  useKey("ArrowLeft", previousExample);
  const allRankings = Object.values(rankings);
  const numUntouched = allRankings.filter(
    ({ ranking }) => ranking.length === 0
  ).length;
  const numDone = allRankings.filter(
    ({ unranked }) => unranked.length === 0
  ).length;
  const numInProgress = allRankings.length - numUntouched - numDone;
  const [instructionModalIsOpen, openInstructionModal, closeInstructionModal] =
    useModal();
  let token;
  if (selectedExampleId === undefined)
    token = <ErrorDisplay chill>nothing selected</ErrorDisplay>;
  else if (selectedIndex.current === -1)
    token = <ErrorDisplay>unknown example id</ErrorDisplay>;
  else
    token = (
      <Example
        key={`${userId}-${selectedExampleId}`}
        entry={rankings[selectedExampleId]}
        modifyRanking={(update) => modifyRanking([selectedExampleId, update])}
      />
    );
  return (
    <div className="flex flex-col h-full">
      <div className="grid grid-cols-[400px_2fr] h-full overflow-hidden">
        <div
          ref={parentRef}
          className="flex flex-col h-full gap-2 overflow-y-auto"
        >
          {orderedRankingKeys.map((thisExampleId, i) => {
            const { example, unranked, ranking } = rankings[thisExampleId];
            return (
              <Link
                ref={thisExampleId === selectedExampleId ? childRef : null}
                key={thisExampleId}
                to={`/${userId}/${thisExampleId}`}
              >
                <ExampleCard
                  isSelected={selectedExampleId === thisExampleId}
                  id={thisExampleId}
                  reference={example.reference}
                  unranked={unranked}
                  ranking={ranking}
                  index={i + 1}
                />
              </Link>
            );
          })}
        </div>
        {token}
      </div>
      <div
        className={`flex gap-2 justify-between items-center border-t-2 border-black p-1 ${
          error ? "bg-red-500" : ""
        }`}
      >
        <div className="flex gap-1">
          <Badge variant="secondary">{numUntouched}</Badge>
          <Badge variant="warning">{numInProgress}</Badge>
          <Badge variant="success">{numDone}</Badge>
        </div>
        <Button variant="warning" small onClick={openInstructionModal}>
          Show Instructions
        </Button>
        <Modal isOpen={instructionModalIsOpen} close={closeInstructionModal}>
          <div className="bg-slate-100 p-5 sticky z-20 top-0 flex flex-wrap justify-between items-center border-b">
            <ModalTitle>Instructions</ModalTitle>
            <div className="flex flex-wrap items-center gap-2">
              <Button
                appearance="soft"
                variant="primary"
                onClick={closeInstructionModal}
              >
                Close
              </Button>
            </div>
          </div>
          <div className="flex flex-col p-5 [&>*:not(:first-child)]:pt-3 [&>*:not(:last-child)]:pb-3 divide-y">
            <p>
              How similar are the small phrases to the reference phrase? Drag
              and drop the boxes with the phrases on the left and bring them in
              your preferred order on the right. The most preferred phrase is on
              the top and the less you prefer a phrase, the lower it should be
              in the ranking.
            </p>
            <p>
              Similarity is less in a sense of exact meaning but much rather in
              a meaning of is there some relation between the reference and
              hypotheses.
            </p>
            <p>
              To get a better understanding of the meaning of the reference, the
              title of the original discussion and some central sentences from
              the cluster are provided (click the "show cluster" button next to
              the reference). The central sentences are selected based on how
              central they are in the original cluster and their mean similarity
              to the reference and hypotheses. So these are not perfectly
              representative to the cluster, but they can help you to get a
              better understanding of some hard to understand meanings.
            </p>
            <p>
              <div>
                <div>
                  <div className="font-bold">
                    Recommended Strategy for judging:
                  </div>
                  <div className="pl-4">
                    <div>
                      <span className="font-bold pr-2">
                        The relation between the reference and hypotheses is
                        understandable:
                      </span>
                      <span>only read the reference and the hypotheses</span>
                    </div>
                    <div>
                      <span className="font-bold pr-2">
                        The reference is a bit weird:
                      </span>
                      <span>
                        read the title to get a better idea in what context the
                        reference is used
                      </span>
                    </div>
                    <div>
                      <span className="font-bold pr-2">
                        The hypotheses are hard to understand:
                      </span>
                      <span>
                        read the central sentences from the cluster for more
                        context
                      </span>
                    </div>
                    <div>
                      <span className="font-bold pr-2">
                        The relation between the reference and hypotheses are
                        not clear:
                      </span>
                      <span>
                        read the central and random sentences from the cluster
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </p>
            <p>
              We are looking for a label that describes the content of a cluster
              of sentences very well. It is important to understand that the
              reference is not the perfect label but much rather something that
              is strongly related to the perfect label.
            </p>
            <p>
              When a lot of hypotheses are talking about something but the
              reference is not mentioning this specific thing, it can be a sign,
              that the reference might not be complete. In that case it might be
              sensible to update the reference with this specific thing (in your
              head).
              <div>
                <div>
                  <div className="font-bold">Example:</div>
                  <div className="pl-4">
                    <div>
                      <span className="font-bold pr-2">Reference:</span>
                      <span>
                        responsibilities between employee and employer
                      </span>
                    </div>
                    <div>
                      <span className="font-bold pr-2">
                        A lot of hypotheses mentioning:
                      </span>
                      <span>the service industry</span>
                    </div>
                    <div>
                      <span className="font-bold pr-2">Reference:</span>
                      <span>
                        responsibilities between employee and employer in the
                        service industry
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </p>
            <p>
              In the end we are looking for the central meaning of the cluster
              and it is very likely that at least one model got the central
              meaning right and the task is to guess what model got the central
              meaning best based on what the reference suggests the best central
              meaning is.
            </p>
          </div>
        </Modal>
        {error && (
          <div className="font-bold text-black">
            an error occurred: "{error}", please report this error
          </div>
        )}
        <div className="flex gap-2 items-center">
          <div className="text-sm text-gray-600">
            you can also use arrow keys to navigate
          </div>
          <Button small onClick={previousExample}>
            previous
          </Button>
          <Button small onClick={nextExample}>
            next
          </Button>
        </div>
      </div>
    </div>
  );
}

function ErrorDisplay({ children, chill }) {
  return (
    <div
      className={`flex h-full items-center justify-center text-6xl ${
        chill ? "" : "bg-red-400 "
      }`}
    >
      {children}
    </div>
  );
}

function Homepage() {
  const { userId, selectedExampleId } = useParams();
  const { loading, value, error } = useAsync(
    () => getExamples(userId),
    [userId]
  );
  if (error) throw error;
  if (loading)
    return (
      <div className="h-full flex items-center justify-center">
        <Loading big />
      </div>
    );
  if (!value.success) return <ErrorDisplay>{value.reason}</ErrorDisplay>;
  const { examples, rankings } = value.data;
  const initialRankings = () =>
    omap(rankings, (ranking, exampleId) => {
      const example = { ...examples[exampleId] };
      const { hypotheses } = example;
      const allKeys = Object.keys(hypotheses);
      const colorIndexes = shuffle([...Array(allKeys.length).keys()]);
      example.colorIndexes = Object.fromEntries(
        allKeys.map((key, i) => [key, colorIndexes[i]])
      );
      const unranked = shuffle(allKeys.filter((v) => !ranking.includes(v)));
      return { example, unranked, ranking };
    });
  return (
    <ExampleList
      examples={examples}
      initialRankings={initialRankings}
      userId={userId}
      selectedExampleId={selectedExampleId}
    />
  );
}

function UnknownRoute() {
  return <div>unknown route</div>;
}

const routes = [
  {
    path: "/:userId?/:selectedExampleId?",
    name: "Homepage",
    element: <Homepage />,
  },
  { path: "*", element: <UnknownRoute /> },
];

function Content() {
  return useRoutes(routes);
}

function App() {
  return (
    <BrowserRouter>
      <div className="h-screen">
        <Content />
      </div>
    </BrowserRouter>
  );
}

export default App;

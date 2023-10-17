import { useCallback, useRef } from "react";

import { defaultdict } from "../python";
import { transpose } from "../util/object";
import { useAsync } from "./async";

async function randomColor(text) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const buffer = await crypto.subtle.digest("SHA-1", data);
  const numbers = new Uint8Array(buffer);
  return numbers.slice(0, 3);
}

function foregroundColor(r, g, b, alpha = 1.0) {
  return r * 0.299 + g * 0.587 + b * 0.114 + (1 - alpha) * 255 > 186
    ? "#000000"
    : "#ffffff";
}

function extractIdsFromComments(comments) {
  const ids = [];
  comments.forEach(({ name, comments: subComments }) => {
    ids.push(name);
    ids.push(...extractIdsFromComments(subComments));
  });
  return ids;
}
const COLORS = [
  [44, 160, 44], // #2ca02c
  [255, 127, 14], // #e57f0e
  [31, 119, 180], // #1f77b4
  [227, 119, 194], // #e377c2
  [127, 127, 127], // #7f7f7f
  [0, 221, 175], // #00ddaf
  [188, 189, 34], // #ddc117
  [209, 23, 103], // #d11767
  [150, 209, 23], // #96d117
  [140, 86, 75], // #8c564b
  [221, 14, 14], // #dd0e0e
  [142, 45, 191], // #8e2dbf
  [23, 190, 207], // #17becf
  [209, 147, 23], // #d19317
  [29, 23, 209], // #1d17d1
  [251, 104, 233], // #fb68e9
  [148, 103, 189], // #9467bd
];

async function clusterToRGB(value) {
  if (value === -2) {
    return [0, 0, 0];
  }
  if (value === -1) {
    return [255, 255, 255];
  }
  if (value < COLORS.length) {
    return COLORS[value];
  }
  return randomColor(value.toString());
}

function RGBToString(r, g, b) {
  return `rgb(${r}, ${g}, ${b})`;
}

function applyAlpha(v, alpha) {
  return Math.round(v * alpha + 255 * (1 - alpha));
}

function applyAlphaToRGB(r, g, b, alpha) {
  return [applyAlpha(r, alpha), applyAlpha(g, alpha), applyAlpha(b, alpha)];
}

async function clusterToColor({ trueValue }) {
  const alpha = trueValue === -1 ? 0.3 : 0.5;
  const [r, g, b] = await clusterToRGB(trueValue);
  return {
    bgText: RGBToString(...applyAlphaToRGB(r, g, b, alpha)),
    bgLight: RGBToString(...applyAlphaToRGB(r, g, b, 0.1)),
    bgNeutral: RGBToString(...applyAlphaToRGB(r, g, b, 0.75)),
    fg: foregroundColor(r, g, b, alpha),
    fill: RGBToString(r, g, b),
  };
}

async function extractClusters(orderedIds, result) {
  const clusters = defaultdict(() => []);
  const points = [];
  orderedIds.forEach((id) => {
    result[id].forEach((e) => {
      clusters[e.labelId].push(e);
      points.push(e);
    });
  });

  let entries = Object.entries(clusters);
  entries = entries.filter(([k]) => k >= 0);
  entries = await Promise.all(
    entries.map(async ([k, elements]) => {
      const key = parseInt(k, 10);
      const [r, g, b] = await clusterToRGB(key);
      return [key, { elements, color: `rgb(${r}, ${g}, ${b})` }];
    })
  );
  entries.sort((a, b) => a[0] - b[0]);
  return [entries, points];
}

function buildMinimap(orderedIds, result) {
  const minimap = [];
  let offset = 0;
  orderedIds.forEach((threadId) => {
    result[threadId].forEach(
      ({
        text: { length },
        id,
        labelId,
        color: { bgNeutral },
        cluster: { value: cluster },
      }) => {
        minimap.push({
          offset,
          length,
          id,
          labelId,
          color: bgNeutral,
          cluster,
        });
        offset += length;
      }
    );
  });
  return minimap;
}

function getClusterSize(clusterId, clusterMap) {
  return clusterMap[clusterId].elements.length;
}

function compareClusters(clusterIdA, clusterIdB, clusterMap) {
  const diff =
    getClusterSize(clusterIdB, clusterMap) -
    getClusterSize(clusterIdA, clusterMap);
  if (diff < 0) return -1;
  if (diff > 0) return 1;
  return clusterIdA - clusterIdB;
}

function groupFrames(frames, clusters) {
  const hasFrames = Boolean(frames);
  const clusterMap = Object.fromEntries(clusters);
  const sortFunc = (a, b) => compareClusters(a, b, clusterMap);
  let order;
  if (hasFrames) {
    order = defaultdict(() => []);
    const noFrame = [];
    Object.entries(frames).forEach(([clusterId, frameLabels]) => {
      if (frameLabels.length) {
        order[frameLabels[0]].push(clusterId);
      } else {
        noFrame.push(clusterId);
      }
    });
    order = Object.entries(order).sort((a, b) => a[0].localeCompare(b[0]));
    if (noFrame.length) {
      order.push(["no frame", noFrame]);
    }
    order.forEach(([, e]) => {
      e.sort(sortFunc);
    });
  } else {
    order = clusters.map(([clusterId]) => clusterId);
    order.sort(sortFunc);
  }
  return {
    order,
    hasFrames,
  };
}

function useThread(thread) {
  const { root, result, frames } = thread;
  const { name, comments } = root;

  const computeStatistics = useCallback(async () => {
    const allSentences = Object.values(result).flat();
    allSentences.forEach((post, i) => {
      post.id = i;
    });
    await Promise.all(
      allSentences.map(async (post) => {
        const { trueValue } = post.cluster;
        post.labelId = trueValue;
        post.color = await clusterToColor(post.cluster);
      })
    );

    const orderedIds = [name, ...extractIdsFromComments(comments)];
    const [clusters, points] = await extractClusters(orderedIds, result);
    const groupedFrames = transpose(frames || {});
    const initialCluster = points.find(
      ({ cluster: { trueValue } }) => trueValue >= 0
    )?.cluster?.trueValue;
    const minimap = buildMinimap(orderedIds, result);
    const elements = allSentences.map((meta) => ({
      highlighted: false,
      active: false,
      sides: {},
      meta,
    }));
    return {
      clusters,
      points,
      elements,
      minimap,
      initialCluster,
      groupedFrames,
    };
  }, [name, comments, result, frames]);
  const { value, loading: computing, error } = useAsync(computeStatistics);

  const { clusters, points, elements, minimap, initialCluster, groupedFrames } =
    value ?? {};

  const currentClusterRef = useRef();

  const setHighlighted = useCallback(
    (eId, highlighted) => {
      const element = elements[eId];
      element.highlighted = highlighted;
      Object.values(element.sides).forEach(
        (e) => e && e.setHighlighted && e.setHighlighted(highlighted)
      );
    },
    [elements]
  );

  const setActive = useCallback(
    (eId, active) => {
      const element = elements[eId];
      element.active = active;
      const { sides } = element;
      Object.values(sides).forEach(
        (e) => e && e.setActive && e.setActive(active)
      );
    },
    [elements]
  );

  const registerElement = useCallback(
    (eId, side, args) => {
      if (elements) {
        const element = elements[eId];
        element.sides[side] = args;
        if (args.canActivate) setActive(eId, true);
        else if (args.setActive) args.setActive(element.active);
        if (args.setHighlighted) args.setHighlighted(element.highlighted);
      }
    },
    [elements, setActive]
  );

  const unregisterElement = useCallback(
    (eId, side) => {
      if (elements) {
        const { canActivate } = elements[eId].sides[side];
        delete elements[eId].sides[side];
        if (canActivate) setActive(eId, false);
      }
    },
    [elements, setActive]
  );

  const isHighlighted = useCallback(
    (eId) => (elements ? elements[eId].highlighted : false),
    [elements]
  );

  const isActive = useCallback(
    (eId) => (elements ? elements[eId].active : false),
    [elements]
  );

  const hover = useCallback(
    (eId) => setHighlighted(eId, true),
    [setHighlighted]
  );

  const unHover = useCallback(
    (eId) => setHighlighted(eId, false),
    [setHighlighted]
  );

  const scrollTo = useCallback(
    (eId, side) => {
      const { current } = currentClusterRef;
      if (current) {
        const { setCurrentCluster } = current;
        setCurrentCluster(elements[eId].meta.labelId);
      }
      return Object.entries(elements[eId].sides).forEach(
        ([i, e]) => i !== side && e && e.scroll && e.scroll()
      );
    },
    [elements]
  );

  return {
    computing,
    error,
    clusters,
    initialCluster,
    groupedFrames,
    registerElement,
    unregisterElement,
    isHighlighted,
    isActive,
    hover,
    unHover,
    scrollTo,
    points,
    minimap,
    currentClusterRef,
  };
}

export {
  useThread,
  groupFrames,
  extractIdsFromComments,
  clusterToColor,
  extractClusters,
};

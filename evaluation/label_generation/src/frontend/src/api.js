import { post, get } from "./request";

async function getExamples(userId) {
  return get(`/api/${userId}`);
}

async function getRanking(userId, exampleId) {
  return get(`/api/${userId}/${exampleId}`);
}

async function updateRanking(userId, exampleId, rankingState) {
  return post(`/api/${userId}/${exampleId}`, rankingState);
}

export { getExamples, getRanking, updateRanking };

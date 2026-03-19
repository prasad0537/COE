const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "";

const FALLBACK_SAMPLE_TEXT = `Senior Data Engineer

We are looking for a Senior Data Engineer with strong Python and SQL skills to build scalable ETL pipelines.
The candidate must have hands-on experience with AWS, Docker, Kubernetes, and CI/CD workflows.
Required experience includes Spark, data modeling, and working with PostgreSQL or Snowflake.
You will collaborate with cross-functional stakeholders and communicate findings clearly.
Nice to have: Terraform, Tableau, and mentoring junior engineers.`;

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new Error("Cannot reach the backend server. Start the full project with run.ps1 or deploy the app.");
  }
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || "Request failed.");
  }

  return data;
}

export function fetchSampleDescription() {
  return request("/api/sample")
    .then((data) => data.text || FALLBACK_SAMPLE_TEXT)
    .catch(() => FALLBACK_SAMPLE_TEXT);
}

export function predictSkills(payload) {
  return request("/api/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export function matchResumeSkills(payload) {
  return request("/api/match", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

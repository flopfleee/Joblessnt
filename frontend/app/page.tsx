"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [keyword, setKeyword] = useState("");
  const [subject, setSubject] = useState("");
  const [location, setLocation] = useState("");
  const [jobType, setJobType] = useState("");
  
  const searchJobs = () => {
  setLoading(true);
  
  const params = new URLSearchParams();

  if (subject) {
    params.append("subject", subject);
  }

  if (location) {
    params.append("location", location);
  }

  if (jobType) {
    params.append("job_type", jobType);
  }

  fetch(`http://127.0.0.1:8000/jobs?${params.toString()}`)
    .then((response) => response.json())
    .then((data) => {
      let filteredJobs = data.jobs;

      if (keyword) {
        filteredJobs = filteredJobs.filter((job: any) =>
          `${job.title} ${job.company} ${job.description}`
            .toLowerCase()
            .includes(keyword.toLowerCase())
        );
      }

      setJobs(filteredJobs);
      setLoading(false);
    })
    .catch((error) => {
      console.error("Failed to fetch jobs:", error);
      setLoading(false);
    });
};

useEffect(() => {
  searchJobs();
}, []);
  
  return (
    <main className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-6 py-5">
          <h1 className="text-2xl font-bold text-gray-900">
            Jobless'nt
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Find internships and placement-year opportunities
          </p>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900">
            Find your next opportunity
          </h2>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <input
               type="text"
               placeholder="Search by keyword..."
               value={keyword}
               onChange={(event) => setKeyword(event.target.value)}
               className="rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-500 outline-none focus:border-blue-500"
             />

            <select
  value={subject}
  onChange={(event) => setSubject(event.target.value)}
  className="rounded-lg border border-gray-300 px-4 py-3 text-gray-900 outline-none focus:border-blue-500"
>
              <option value="">All subjects</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Software Engineering">
                Software Engineering
              </option>
              <option value="Finance">Finance</option>
              <option value="Business">Business</option>
              <option value="Engineering">Engineering</option>
              <option value="Marketing">Marketing</option>
              <option value="Mathematics">Mathematics</option>
            </select>

            <select
  value={location}
  onChange={(event) => setLocation(event.target.value)}
  className="rounded-lg border border-gray-300 px-4 py-3 text-gray-900 outline-none focus:border-blue-500"
>
              <option value="">All locations</option>
              <option value="London">London</option>
              <option value="Manchester">Manchester</option>
              <option value="Birmingham">Birmingham</option>
            </select>
          </div>

          <div className="mt-4 flex gap-4">
            <select
  value={jobType}
  onChange={(event) => setJobType(event.target.value)}
  className="rounded-lg border border-gray-300 px-4 py-3 text-gray-900 outline-none focus:border-blue-500"
>
              <option value="">All opportunity types</option>
              <option value="internship">Summer Internship</option>
              <option value="placement">Placement Year</option>
              <option value="graduate">Graduate Role</option>
            </select>

            <button
  onClick={searchJobs}
  className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
>
  Search
</button>

<button
  onClick={() => {
    setKeyword("");
    setSubject("");
    setLocation("");
    setJobType("");
    setLoading(true);

    fetch("http://127.0.0.1:8000/jobs")
      .then((response) => response.json())
      .then((data) => {
        setJobs(data.jobs);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Failed to reset jobs:", error);
        setLoading(false);
      });
  }}
  className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50"
>
  Reset
</button>
          </div>
        </div>

        <div className="mt-8">
  <div className="flex items-center justify-between">
  <h2 className="text-xl font-semibold text-gray-900">
    Latest opportunities
  </h2>

  {!loading && (
    <p className="text-sm text-gray-600">
      {jobs.length} {jobs.length === 1 ? "opportunity" : "opportunities"} found
    </p>
  )}
</div>

  {loading ? (
    <p className="mt-4 text-gray-600">Loading opportunities...</p>
  ) : (
    <div className="mt-4 grid gap-4">
      {jobs.map((job) => (
        <div
          key={job.id}
          className="rounded-xl bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-gray-900">
            {job.title}
          </h3>

          <p className="mt-2 text-gray-600">
            {job.company} · {job.city} · {job.duration_months} months
          </p>

          <p className="mt-2 text-sm text-gray-500">
  {job.salary_min != null && job.salary_max != null
    ? `£${job.salary_min.toLocaleString()} - £${job.salary_max.toLocaleString()}`
    : job.salary_min != null
      ? `From £${job.salary_min.toLocaleString()}`
      : job.salary_max != null
        ? `Up to £${job.salary_max.toLocaleString()}`
        : "Salary not specified"}{" "}
  · {job.work_mode}
</p>

          <p className="mt-2 text-sm text-gray-500">
            Deadline: {job.deadline}
          </p>

          <a
            href={job.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            View opportunity
          </a>
        </div>
      ))}
    </div>
  )}
</div>
      </section>
    </main>
  );
}
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatPanel from "../components/ChatPanel";
import CourseSidebar from "../components/CourseSidebar";
import FileUploadPanel from "../components/FileUploadPanel";

const COURSES = [
  {
    id: "mech-101",
    name: "Mechatronics",
    code: "MECH 101",
  },
  {
    id: "calc-101",
    name: "Calculus 1",
    code: "MATH 101",
  },
  {
    id: "ml-200",
    name: "Machine Learning",
    code: "CS 200",
  },
  {
    id: "dl-250",
    name: "Deep Learning",
    code: "CS 250",
  },
];

const TOUR_STORAGE_KEY = "student_dashboard_tour_seen";

const TOUR_STEPS = [
  {
    key: "courses",
    title: "Choose a course",
    description:
      "Use the left panel to switch between courses. Your chat context updates to match the selected class.",
  },
  {
    key: "chat",
    title: "Ask the AI tutor",
    description:
      "Use the center chat panel to ask questions. You can type in the input box or tap the voice button.",
  },
  {
    key: "documents",
    title: "Add document context",
    description:
      "Upload notes or assignments on the right, then select files to provide context for better AI help.",
  },
];

function DashboardPage() {
  const navigate = useNavigate();
  const [selectedCourseId, setSelectedCourseId] = useState(COURSES[0].id);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [tourStepIndex, setTourStepIndex] = useState(-1);

  const selectedCourse = useMemo(
    () => COURSES.find((course) => course.id === selectedCourseId) ?? COURSES[0],
    [selectedCourseId],
  );

  function handleLogout() {
    sessionStorage.removeItem("student_auth");
    navigate("/");
  }

  useEffect(() => {
    const hasSeenTour = localStorage.getItem(TOUR_STORAGE_KEY) === "true";
    if (!hasSeenTour) {
      setTourStepIndex(0);
    }
  }, []);

  function closeTour() {
    setTourStepIndex(-1);
    localStorage.setItem(TOUR_STORAGE_KEY, "true");
  }

  function nextTourStep() {
    if (tourStepIndex >= TOUR_STEPS.length - 1) {
      closeTour();
      return;
    }
    setTourStepIndex((prev) => prev + 1);
  }

  function previousTourStep() {
    setTourStepIndex((prev) => Math.max(0, prev - 1));
  }

  function startTour() {
    setTourStepIndex(0);
  }

  const activeTourStep = tourStepIndex >= 0 ? TOUR_STEPS[tourStepIndex] : null;
  const isTourOpen = activeTourStep !== null;

  const coursesHighlightClass =
    activeTourStep?.key === "courses"
      ? "tour-highlight"
      : isTourOpen
        ? "tour-muted"
        : "";
  const chatHighlightClass =
    activeTourStep?.key === "chat"
      ? "tour-highlight"
      : isTourOpen
        ? "tour-muted"
        : "";
  const docsHighlightClass =
    activeTourStep?.key === "documents"
      ? "tour-highlight"
      : isTourOpen
        ? "tour-muted"
        : "";

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#26648E] via-[#4F8FC0] to-[#53D2DC] p-4 text-white md:p-6">
      <div className="orb orb-one" />
      <div className="orb orb-two" />

      <section className="relative z-10 mx-auto mb-4 flex w-full max-w-[1400px] justify-end">
        <button
          type="button"
          onClick={startTour}
          className="cursor-pointer rounded-full border border-[#FFE3B3]/60 bg-[#FFE3B3]/20 px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-[#FFF1D5] transition hover:bg-[#FFE3B3]/30"
        >
          Take app tour
        </button>
      </section>

      <section className="relative z-10 mx-auto flex w-full max-w-[1400px] flex-col gap-4 lg:h-[calc(100vh-7rem)] lg:grid lg:grid-cols-12 lg:gap-5">
        <CourseSidebar
          courses={COURSES}
          selectedCourseId={selectedCourse.id}
          onSelectCourse={setSelectedCourseId}
          onLogout={handleLogout}
          panelClassName={coursesHighlightClass}
        />
        <ChatPanel
          courseName={selectedCourse.name}
          selectedCourseId={selectedCourse.id}
          selectedDocuments={selectedDocuments}
          panelClassName={chatHighlightClass}
        />
        <FileUploadPanel
          onDocumentsSelect={setSelectedDocuments}
          panelClassName={docsHighlightClass}
        />
      </section>

      {isTourOpen ? (
        <div className="fixed bottom-6 right-6 z-40 w-full max-w-sm rounded-2xl border border-[#FFE3B3]/70 bg-[#1f4d6f]/95 p-5 shadow-2xl">
          <p className="text-xs font-semibold uppercase tracking-wide text-[#FFE3B3]">
            App tour {tourStepIndex + 1}/{TOUR_STEPS.length}
          </p>
          <h3 className="mt-2 text-lg font-semibold text-[#FFF1D5]">
            {activeTourStep.title}
          </h3>
          <p className="mt-2 text-sm leading-6 text-[#E8F7FB]">
            {activeTourStep.description}
          </p>
          <div className="mt-4 flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={closeTour}
              className="cursor-pointer rounded-lg border border-[#FFE3B3]/45 px-3 py-1.5 text-xs font-medium text-[#FFE3B3] transition hover:bg-[#FFE3B3]/15"
            >
              Skip
            </button>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={previousTourStep}
                disabled={tourStepIndex === 0}
                className="cursor-pointer rounded-lg border border-[#53D2DC]/45 px-3 py-1.5 text-xs font-medium text-[#D7EEF8] transition hover:bg-[#53D2DC]/15 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Back
              </button>
              <button
                type="button"
                onClick={nextTourStep}
                className="cursor-pointer rounded-lg bg-[#FFE3B3] px-3 py-1.5 text-xs font-semibold text-[#1f4d6f] transition hover:bg-[#fff0cf]"
              >
                {tourStepIndex === TOUR_STEPS.length - 1 ? "Finish" : "Next"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}

export default DashboardPage;

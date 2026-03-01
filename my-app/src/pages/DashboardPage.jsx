import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatPanel from "../components/ChatPanel";
import CourseSidebar from "../components/CourseSidebar";
import FileUploadPanel from "../components/FileUploadPanel";
import MistakesPanel from "../components/MistakesPanel";
import StudyPlanPanel from "../components/StudyPlanPanel";
import WeeklyReviewPanel from "../components/WeeklyReviewPanel";
import GeneratePanel from "../components/GeneratePanel";
import CanvasImportModal from "../components/CanvasImportModal";

const INITIAL_COURSES = [];

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
  const [courses, setCourses] = useState(INITIAL_COURSES);
  const [selectedCourseId, setSelectedCourseId] = useState(INITIAL_COURSES[0]?.id || null);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [isCanvasModalOpen, setIsCanvasModalOpen] = useState(false);
  const [isAddCourseModalOpen, setIsAddCourseModalOpen] = useState(false);
  const [selectedLearningView, setSelectedLearningView] = useState(null);
  const [tourStepIndex, setTourStepIndex] = useState(-1);

  const selectedCourse = useMemo(
    () => courses.find((course) => course.id === selectedCourseId) || courses[0] || null,
    [selectedCourseId, courses],
  );

  function handleLogout() {
    sessionStorage.removeItem("student_auth");
    navigate("/");
  }

  function handleAddCourse(newCourse) {
    const courseWithId = {
      ...newCourse,
      id: `course-${Date.now()}`,
    };
    setCourses(prev => [...prev, courseWithId]);
    setSelectedCourseId(courseWithId.id);
    setIsAddCourseModalOpen(false);
  }

  function handleDeleteCourse(courseId) {
    if (courses.length <= 1) {
      alert("You must have at least one course");
      return;
    }

    if (confirm("Are you sure you want to delete this course?")) {
      setCourses(prev => prev.filter(c => c.id !== courseId));

      // If we deleted the selected course, select the first remaining one
      if (selectedCourseId === courseId) {
        const remaining = courses.filter(c => c.id !== courseId);
        setSelectedCourseId(remaining[0]?.id || null);
      }
    }
  }

  async function handleCanvasImport(apiKey) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch('/api/canvas-sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to sync with Canvas');
      }

      const data = await response.json();
      const { courses: importedCourses, documents } = data;
      
      // Merge Canvas courses with existing courses (avoid duplicates)
      setCourses(prevCourses => {
        const existingIds = new Set(prevCourses.map(c => c.id));
        const newCourses = importedCourses.filter(c => !existingIds.has(c.id));
        return [...prevCourses, ...newCourses];
      });
      
      // Select the first Canvas course if we added any
      if (importedCourses.length > 0) {
        setSelectedCourseId(importedCourses[0].id);
      }
      
      // Show success message
      alert(`Successfully imported ${importedCourses.length} courses and ${documents.length} documents from Canvas!`);
      
      // Trigger document list refresh
      window.dispatchEvent(new Event('canvas-import-complete'));
      
    } catch (error) {
      console.error("Error importing from Canvas:", error);
      if (error?.name === "AbortError") {
        throw new Error("Canvas import timed out. Please try again.");
      }
      throw error;
    }
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

      <section className="relative z-10 mx-auto mb-4 flex w-full max-w-[1400px] justify-end gap-3">
        <button
          type="button"
          onClick={() => setIsCanvasModalOpen(true)}
          className="cursor-pointer rounded-full border border-[#53D2DC]/60 bg-[#53D2DC]/20 px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-[#D7EEF8] transition hover:bg-[#53D2DC]/30"
        >
          Import from Canvas
        </button>
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
          courses={courses}
          selectedCourseId={selectedCourse?.id}
          onSelectCourse={setSelectedCourseId}
          onLogout={handleLogout}
          selectedLearningView={selectedLearningView}
          onSelectLearningView={setSelectedLearningView}
          onAddCourse={() => setIsAddCourseModalOpen(true)}
          onDeleteCourse={handleDeleteCourse}
          panelClassName={coursesHighlightClass}
        />
        {selectedLearningView && selectedCourse && (
          <div className={`lg:col-span-9 lg:min-h-0 ${chatHighlightClass}`}>
            {selectedLearningView === "mistakes" && (
              <MistakesPanel courseName={selectedCourse.name} />
            )}
            {selectedLearningView === "study-plan" && <StudyPlanPanel />}
            {selectedLearningView === "weekly-review" && (
              <WeeklyReviewPanel courseName={selectedCourse.name} />
            )}
            {selectedLearningView === "generate" && (
              <GeneratePanel
                courseName={selectedCourse.name}
                selectedDocuments={selectedDocuments}
              />
            )}
          </div>
        )}
        {!selectedLearningView && selectedCourse && (
          <>
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
          </>
        )}
        {!selectedLearningView && !selectedCourse && (
          <div className="lg:col-span-9 flex items-center justify-center rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-8 shadow-xl backdrop-blur-xl">
            <div className="text-center">
              <p className="text-xl font-semibold text-white mb-4">No courses yet</p>
              <p className="text-sm text-[#EAF9FD] mb-6">Get started by adding your first course</p>
              <button
                type="button"
                onClick={() => setIsAddCourseModalOpen(true)}
                className="rounded-lg bg-[#FFE3B3] px-6 py-2.5 text-sm font-semibold text-[#1f4d6f] transition hover:bg-[#fff0cf]"
              >
                Add Your First Course
              </button>
            </div>
          </div>
        )}
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

      {/* Add Course Modal */}
      {isAddCourseModalOpen && (
        <AddCourseModal
          onClose={() => setIsAddCourseModalOpen(false)}
          onAdd={handleAddCourse}
        />
      )}

      {/* Canvas Import Modal */}
      <CanvasImportModal
        isOpen={isCanvasModalOpen}
        onClose={() => setIsCanvasModalOpen(false)}
        onImport={handleCanvasImport}
      />
    </main>
  );
}

function AddCourseModal({ onClose, onAdd }) {
  const [courseName, setCourseName] = useState("");
  const [courseCode, setCourseCode] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!courseName.trim() || !courseCode.trim()) {
      alert("Please fill in both course name and code");
      return;
    }
    onAdd({ name: courseName.trim(), code: courseCode.trim() });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-2xl border border-[#FFE3B3]/30 bg-[#26648E] p-6 shadow-2xl">
        <h2 className="mb-4 text-xl font-bold text-white">Add New Course</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-[#FFE3B3]">
              Course Name
            </label>
            <input
              type="text"
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              placeholder="e.g., Linear Algebra"
              className="w-full rounded-lg border border-[#53D2DC]/30 bg-[#1f4d6f]/50 px-3 py-2 text-white placeholder-gray-400 focus:border-[#FFE3B3] focus:outline-none focus:ring-1 focus:ring-[#FFE3B3]"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-[#FFE3B3]">
              Course Code
            </label>
            <input
              type="text"
              value={courseCode}
              onChange={(e) => setCourseCode(e.target.value)}
              placeholder="e.g., MATH 250"
              className="w-full rounded-lg border border-[#53D2DC]/30 bg-[#1f4d6f]/50 px-3 py-2 text-white placeholder-gray-400 focus:border-[#FFE3B3] focus:outline-none focus:ring-1 focus:ring-[#FFE3B3]"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-[#FFE3B3]/40 px-4 py-2 text-sm font-medium text-[#FFE3B3] transition hover:bg-[#FFE3B3]/10"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 rounded-lg bg-[#FFE3B3] px-4 py-2 text-sm font-semibold text-[#1f4d6f] transition hover:bg-[#fff0cf]"
            >
              Add Course
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DashboardPage;

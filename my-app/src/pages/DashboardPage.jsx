import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatPanel from "../components/ChatPanel";
import CourseSidebar from "../components/CourseSidebar";
import FileUploadPanel from "../components/FileUploadPanel";

const COURSES = [
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

function DashboardPage() {
  const navigate = useNavigate();
  const [selectedCourseId, setSelectedCourseId] = useState(COURSES[0].id);
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  const selectedCourse = useMemo(
    () => COURSES.find((course) => course.id === selectedCourseId) ?? COURSES[0],
    [selectedCourseId],
  );

  function handleLogout() {
    sessionStorage.removeItem("student_auth");
    navigate("/");
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#26648E] via-[#4F8FC0] to-[#53D2DC] p-4 text-white md:p-6">
      <div className="orb orb-one" />
      <div className="orb orb-two" />

      <section className="relative z-10 mx-auto flex w-full max-w-[1400px] flex-col gap-4 lg:h-[calc(100vh-3rem)] lg:grid lg:grid-cols-12 lg:gap-5">
        <CourseSidebar
          courses={COURSES}
          selectedCourseId={selectedCourse.id}
          onSelectCourse={setSelectedCourseId}
          onLogout={handleLogout}
        />
        <ChatPanel courseName={selectedCourse.name} selectedCourseId={selectedCourse.id} selectedDocuments={selectedDocuments} />
        <FileUploadPanel onDocumentsSelect={setSelectedDocuments} />
      </section>
    </main>
  );
}

export default DashboardPage;

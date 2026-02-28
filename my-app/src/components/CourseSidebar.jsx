const LEARNING_VIEWS = [
  { id: "mistakes", label: "My mistakes" },
  { id: "study-plan", label: "Study plan" },
  { id: "weekly-review", label: "Weekly review" },
  { id: "generate", label: "Generate materials" },
];

function CourseSidebar({
  courses,
  selectedCourseId,
  onSelectCourse,
  onLogout,
  selectedLearningView,
  onSelectLearningView,
  panelClassName = "",
}) {
  return (
    <aside className={`fade-in-up flex min-h-[320px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-3 lg:min-h-0 ${panelClassName}`}>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">Courses</p>
          <h2 className="text-lg font-semibold text-white">My classes</h2>
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="cursor-pointer rounded-lg border border-[#FFE3B3]/60 px-3 py-1.5 text-xs font-medium text-[#FFE3B3] transition-all duration-300 hover:bg-[#FFE3B3]/20"
        >
          Log out
        </button>
      </div>

      <div className="space-y-2 lg:min-h-0 lg:flex-1 lg:overflow-y-auto lg:pr-1">
        {courses.map((course) => {
          const isSelected = selectedCourseId === course.id && !selectedLearningView;
          return (
            <button
              key={course.id}
              type="button"
              onClick={() => {
                onSelectLearningView?.(null);
                onSelectCourse(course.id);
              }}
              className={`group flex w-full cursor-pointer items-center justify-between rounded-xl border px-3 py-3 text-left text-sm transition-all duration-300 ${
                isSelected
                  ? "border-[#FFE3B3]/80 bg-[#FFE3B3]/30 text-white shadow-md shadow-[#26648E]/40"
                  : "border-[#53D2DC]/30 bg-[#26648E]/45 text-[#EAF9FD] hover:-translate-y-0.5 hover:border-[#FFE3B3]/55 hover:bg-[#4F8FC0]/35"
              }`}
            >
              <div className="min-w-0">
                <p className="truncate font-semibold">{course.name}</p>
                <p className="mt-1 inline-block rounded-md bg-[#FFE3B3]/20 px-2 py-0.5 text-[11px] text-[#FFE3B3]">
                  {course.code}
                </p>
              </div>
              <span
                className={`ml-3 text-base transition-transform duration-300 ${
                  isSelected
                    ? "translate-x-0 text-[#FFE3B3]"
                    : "text-[#A9D6E6] group-hover:translate-x-0.5 group-hover:text-[#FFE3B3]"
                }`}
                aria-hidden="true"
              >
                →
              </span>
            </button>
          );
        })}
        <div className="mt-4 border-t border-[#FFE3B3]/25 pt-3">
          <p className="mb-2 text-xs uppercase tracking-wide text-[#FFE3B3]">Learning</p>
          {LEARNING_VIEWS.map((view) => {
            const isActive = selectedLearningView === view.id;
            return (
              <button
                key={view.id}
                type="button"
                onClick={() => onSelectLearningView?.(isActive ? null : view.id)}
                className={`mb-1.5 flex w-full cursor-pointer items-center rounded-lg border px-2 py-2 text-left text-sm transition-all ${
                  isActive
                    ? "border-[#FFE3B3]/60 bg-[#FFE3B3]/25 text-[#FFE3B3]"
                    : "border-[#53D2DC]/20 bg-[#26648E]/40 text-[#E8F7FB] hover:bg-[#4F8FC0]/30"
                }`}
              >
                {view.label}
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}

export default CourseSidebar;

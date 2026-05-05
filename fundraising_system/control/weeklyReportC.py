from entity.report import Report


class WeeklyReportController:
    def generate_weekly_report(self, selected_week_start):
        return Report.generate_report("weekly", selected_week_start)
// ============================================================================
// Enterprise Financial Analytics Platform (EFAP)
// ----------------------------------------------------------------------------
// Object          : Dim_Date
// Object Type     : Conformed Dimension
// Layer           : Semantic Layer
// Version         : 1.0.0
// Status          : Implemented
// ----------------------------------------------------------------------------
// Description:
// Enterprise calendar dimension for Power BI semantic model.
// One row represents one calendar day.
// ============================================================================
let
    // =========================================================================
    // Configuration
    // =========================================================================
    StartYear = 2020,
    EndYear = 2035,
    FiscalYearStartMonth = 1,
    Culture = "en-US",
    StartDate = #date(StartYear, 1, 1),
    EndDate = #date(EndYear, 12, 31),
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    // =========================================================================
    // Calendar
    // =========================================================================
    DateList = List.Dates(StartDate, NumberOfDays, #duration(1, 0, 0, 0)),
    Calendar = Table.FromList(DateList, Splitter.SplitByNothing(), {"FullDate"}, null, ExtraValues.Error),
    // =========================================================================
    // Date Key
    // =========================================================================
    AddDateKey = Table.AddColumn(
        Calendar,
        "DateKey",
        each Date.Year([FullDate]) * 10000 + Date.Month([FullDate]) * 100 + Date.Day([FullDate]),
        Int64.Type
    ),
    // =========================================================================
    // Day Attributes
    // =========================================================================
    AddDay = Table.AddColumn(AddDateKey, "Day", each Date.Day([FullDate]), Int64.Type),
    AddDayName = Table.AddColumn(AddDay, "DayName", each Date.ToText([FullDate], "dddd", Culture), type text),
    AddDayShortName = Table.AddColumn(
        AddDayName, "DayShortName", each Date.ToText([FullDate], "ddd", Culture), type text
    ),
    AddDayOfWeek = Table.AddColumn(
        AddDayShortName, "DayOfWeek", each Date.DayOfWeek([FullDate], Day.Monday) + 1, Int64.Type
    ),
    AddISOWeek = Table.AddColumn(AddDayOfWeek, "ISOWeek", each Date.WeekOfYear([FullDate], Day.Monday), Int64.Type),
    // =========================================================================
    // Calendar Attributes
    // =========================================================================
    AddCalendarMonth = Table.AddColumn(AddISOWeek, "CalendarMonth", each Date.Month([FullDate]), Int64.Type),
    AddMonthName = Table.AddColumn(
        AddCalendarMonth, "MonthName", each Date.ToText([FullDate], "MMMM", Culture), type text
    ),
    AddMonthShortName = Table.AddColumn(
        AddMonthName, "MonthShortName", each Date.ToText([FullDate], "MMM", Culture), type text
    ),
    AddCalendarQuarter = Table.AddColumn(
        AddMonthShortName, "CalendarQuarter", each Date.QuarterOfYear([FullDate]), Int64.Type
    ),
    AddQuarterName = Table.AddColumn(
        AddCalendarQuarter, "QuarterName", each "Q" & Text.From(Date.QuarterOfYear([FullDate])), type text
    ),
    AddCalendarYear = Table.AddColumn(AddQuarterName, "CalendarYear", each Date.Year([FullDate]), Int64.Type),
    // =========================================================================
    // Fiscal Attributes
    // =========================================================================
    AddFiscalMonth = Table.AddColumn(
        AddCalendarYear,
        "FiscalMonth",
        each
            if [CalendarMonth] >= FiscalYearStartMonth then
                [CalendarMonth] - FiscalYearStartMonth + 1
            else
                [CalendarMonth] + (12 - FiscalYearStartMonth + 1),
        Int64.Type
    ),
    AddFiscalQuarter = Table.AddColumn(
        AddFiscalMonth, "FiscalQuarter", each Number.RoundUp([FiscalMonth] / 3), Int64.Type
    ),
    AddFiscalYear = Table.AddColumn(
        AddFiscalQuarter,
        "FiscalYear",
        each if [CalendarMonth] >= FiscalYearStartMonth then [CalendarYear] else [CalendarYear] - 1,
        Int64.Type
    ),
    // =========================================================================
    // Period Attributes
    // =========================================================================
    AddYearMonth = Table.AddColumn(
        AddFiscalYear,
        "YearMonth",
        each Text.From([CalendarYear]) & "-" & Text.PadStart(Text.From([CalendarMonth]), 2, "0"),
        type text
    ),
    AddYearMonthKey = Table.AddColumn(
        AddYearMonth, "YearMonthKey", each [CalendarYear] * 100 + [CalendarMonth], Int64.Type
    ),
    // =========================================================================
    // Period Start Dates
    // =========================================================================
    AddMonthStartDate = Table.AddColumn(
        AddYearMonthKey, "MonthStartDate", each Date.StartOfMonth([FullDate]), type date
    ),
    AddMonthEndDate = Table.AddColumn(AddMonthStartDate, "MonthEndDate", each Date.EndOfMonth([FullDate]), type date),
    AddQuarterStartDate = Table.AddColumn(
        AddMonthEndDate, "QuarterStartDate", each Date.StartOfQuarter([FullDate]), type date
    ),
    AddQuarterEndDate = Table.AddColumn(
        AddQuarterStartDate, "QuarterEndDate", each Date.EndOfQuarter([FullDate]), type date
    ),
    AddYearStartDate = Table.AddColumn(
        AddQuarterEndDate, "YearStartDate", each Date.StartOfYear([FullDate]), type date
    ),
    AddYearEndDate = Table.AddColumn(AddYearStartDate, "YearEndDate", each Date.EndOfYear([FullDate]), type date),
    // =========================================================================
    // Business Flags
    // =========================================================================
    AddIsWeekend = Table.AddColumn(AddYearEndDate, "IsWeekend", each [DayOfWeek] >= 6, type logical),
    AddIsWorkingDay = Table.AddColumn(AddIsWeekend, "IsWorkingDay", each not [IsWeekend], type logical),
    AddIsMonthEnd = Table.AddColumn(AddIsWorkingDay, "IsMonthEnd", each [FullDate] = [MonthEndDate], type logical),
    AddIsQuarterEnd = Table.AddColumn(AddIsMonthEnd, "IsQuarterEnd", each [FullDate] = [QuarterEndDate], type logical),
    AddIsYearEnd = Table.AddColumn(AddIsQuarterEnd, "IsYearEnd", each [FullDate] = [YearEndDate], type logical),
    // =========================================================================
    // Current Period Flags
    // =========================================================================
    Today = Date.From(DateTime.LocalNow()),
    CurrentYear = Date.Year(Today),
    CurrentMonth = Date.Month(Today),
    CurrentQuarter = Date.QuarterOfYear(Today),
    AddIsCurrentDate = Table.AddColumn(AddIsYearEnd, "IsCurrentDate", each [FullDate] = Today, type logical),
    AddIsCurrentMonth = Table.AddColumn(
        AddIsCurrentDate,
        "IsCurrentMonth",
        each [CalendarYear] = CurrentYear and [CalendarMonth] = CurrentMonth,
        type logical
    ),
    AddIsCurrentQuarter = Table.AddColumn(
        AddIsCurrentMonth,
        "IsCurrentQuarter",
        each [CalendarYear] = CurrentYear and [CalendarQuarter] = CurrentQuarter,
        type logical
    ),
    AddIsCurrentYear = Table.AddColumn(
        AddIsCurrentQuarter, "IsCurrentYear", each [CalendarYear] = CurrentYear, type logical
    ),
    // =========================================================================
    // Final Column Order
    // =========================================================================
    FinalTable = Table.ReorderColumns(
        AddIsCurrentYear,
        {
            "DateKey",
            "FullDate",
            "Day",
            "DayName",
            "DayShortName",
            "DayOfWeek",
            "ISOWeek",
            "CalendarMonth",
            "MonthName",
            "MonthShortName",
            "CalendarQuarter",
            "QuarterName",
            "CalendarYear",
            "FiscalMonth",
            "FiscalQuarter",
            "FiscalYear",
            "YearMonth",
            "YearMonthKey",
            "MonthStartDate",
            "MonthEndDate",
            "QuarterStartDate",
            "QuarterEndDate",
            "YearStartDate",
            "YearEndDate",
            "IsWeekend",
            "IsWorkingDay",
            "IsMonthEnd",
            "IsQuarterEnd",
            "IsYearEnd",
            "IsCurrentDate",
            "IsCurrentMonth",
            "IsCurrentQuarter",
            "IsCurrentYear"
        }
    )
in
    FinalTable

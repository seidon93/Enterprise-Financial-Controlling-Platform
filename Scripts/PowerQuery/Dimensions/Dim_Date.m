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

    NumberOfDays =
        Duration.Days(
            EndDate - StartDate
        ) + 1,

    // =========================================================================
    // Calendar
    // =========================================================================

    DateList =
        List.Dates(
            StartDate,
            NumberOfDays,
            #duration(1,0,0,0)
        ),

    Calendar =
        Table.FromList(
            DateList,
            Splitter.SplitByNothing(),
            {"FullDate"},
            null,
            ExtraValues.Error
        ),

    // =========================================================================
    // Date Key
    // =========================================================================

    AddDateKey =
        Table.AddColumn(
            Calendar,
            "DateKey",
            each
                Date.Year([FullDate]) * 10000 +
                Date.Month([FullDate]) * 100 +
                Date.Day([FullDate]),
            Int64.Type
        ),

    // =========================================================================
    // Day Attributes
    // =========================================================================

    AddDay =
        Table.AddColumn(
            AddDateKey,
            "Day",
            each Date.Day([FullDate]),
            Int64.Type
        ),

    AddDayName =
        Table.AddColumn(
            AddDay,
            "DayName",
            each Date.ToText([FullDate], "dddd", Culture),
            type text
        ),

    AddDayShortName =
        Table.AddColumn(
            AddDayName,
            "DayShortName",
            each Date.ToText([FullDate], "ddd", Culture),
            type text
        ),

    AddDayOfWeek =
        Table.AddColumn(
            AddDayShortName,
            "DayOfWeek",
            each Date.DayOfWeek([FullDate], Day.Monday) + 1,
            Int64.Type
        ),

    AddISOWeek =
        Table.AddColumn(
            AddDayOfWeek,
            "ISOWeek",
            each Date.WeekOfYear([FullDate], Day.Monday),
            Int64.Type
        ),

    // =========================================================================
    // Calendar Attributes
    // =========================================================================

    AddCalendarMonth =
        Table.AddColumn(
            AddISOWeek,
            "CalendarMonth",
            each Date.Month([FullDate]),
            Int64.Type
        ),

    AddMonthName =
        Table.AddColumn(
            AddCalendarMonth,
            "MonthName",
            each Date.ToText([FullDate], "MMMM", Culture),
            type text
        ),

    AddMonthShortName =
        Table.AddColumn(
            AddMonthName,
            "MonthShortName",
            each Date.ToText([FullDate], "MMM", Culture),
            type text
        ),

    AddCalendarQuarter =
        Table.AddColumn(
            AddMonthShortName,
            "CalendarQuarter",
            each Date.QuarterOfYear([FullDate]),
            Int64.Type
        ),

    AddQuarterName =
        Table.AddColumn(
            AddCalendarQuarter,
            "QuarterName",
            each "Q" & Text.From(Date.QuarterOfYear([FullDate])),
            type text
        ),

    AddCalendarYear =
        Table.AddColumn(
            AddQuarterName,
            "CalendarYear",
            each Date.Year([FullDate]),
            Int64.Type
        )
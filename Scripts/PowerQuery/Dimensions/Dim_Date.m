// ============================================================================
// Enterprise Financial Analytics Platform (EFAP)
// ----------------------------------------------------------------------------
// Object          : Dim_Date
// Object Type     : Conformed Dimension
// Layer           : Semantic Layer
// Version         : 1.0.0
// Status          : Implemented
// Author          : Project Team
// Created         : 2026-07-09
// Last Updated    : 2026-07-09
//
// Description:
// Enterprise calendar dimension used across all fact tables.
//
// Business Grain:
// One record represents one calendar day.
//
// Dependencies:
// None
//
// Related Documents:
// - EFAP-DIM-001 (Dim_Date Specification)
// - EFAP-LDM-001 (Logical Data Model)
// - EFAP-DD-001  (Data Dictionary)
//
// ============================================================================

let

    // ========================================================================
    // Configuration
    // ========================================================================

    StartYear = 2020,

    EndYear = 2035,

    FiscalYearStartMonth = 1,

    Culture = "en-US",

    StartDate =
        #date(
            StartYear,
            1,
            1
        ),

    EndDate =
        #date(
            EndYear,
            12,
            31
        ),

    TotalDays =
        Duration.Days(
            EndDate - StartDate
        ) + 1,

    // ========================================================================
    // Calendar
    // ========================================================================

    Calendar =
        List.Dates(
            StartDate,
            TotalDays,
            #duration(1,0,0,0)
        ),

    CalendarTable =
        Table.FromList(
            Calendar,
            Splitter.SplitByNothing(),
            {"FullDate"},
            null,
            ExtraValues.Error
        ),

    // ========================================================================
    // Keys
    // ========================================================================

    CalendarWithKeys =
        Table.AddColumn(
            CalendarTable,
            "DateKey",
            each
                Date.Year([FullDate]) * 10000 +
                Date.Month([FullDate]) * 100 +
                Date.Day([FullDate]),
            Int64.Type
        ),

    // ========================================================================
    // Day Attributes
    // ========================================================================

    CalendarWithDayAttributes =
        CalendarWithKeys

        |> Table.AddColumn(
            _,
            "Day",
            each Date.Day([FullDate]),
            Int64.Type
        )

        |> Table.AddColumn(
            _,
            "DayName",
            each Date.ToText(
                [FullDate],
                "dddd",
                Culture
            ),
            type text
        )

        |> Table.AddColumn(
            _,
            "DayShortName",
            each Date.ToText(
                [FullDate],
                "ddd",
                Culture
            ),
            type text
        )

        |> Table.AddColumn(
            _,
            "DayOfWeek",
            each Date.DayOfWeek(
                    [FullDate],
                    Day.Monday
                ) + 1,
            Int64.Type
        )

        |> Table.AddColumn(
            _,
            "ISOWeek",
            each Date.WeekOfYear(
                [FullDate],
                Day.Monday
            ),
            Int64.Type
        ),

    // ========================================================================
    // Calendar Attributes
    // ========================================================================

    CalendarWithCalendarAttributes =
        CalendarWithDayAttributes

        |> Table.AddColumn(
            _,
            "CalendarMonth",
            each Date.Month([FullDate]),
            Int64.Type
        )

        |> Table.AddColumn(
            _,
            "MonthName",
            each Date.ToText(
                [FullDate],
                "MMMM",
                Culture
            ),
            type text
        )

        |> Table.AddColumn(
            _,
            "MonthShortName",
            each Date.ToText(
                [FullDate],
                "MMM",
                Culture
            ),
            type text
        )

        |> Table.AddColumn(
            _,
            "CalendarQuarter",
            each Date.QuarterOfYear([FullDate]),
            Int64.Type
        )

        |> Table.AddColumn(
            _,
            "QuarterName",
            each
                "Q" &
                Text.From(
                    Date.QuarterOfYear([FullDate])
                ),
            type text
        )

        |> Table.AddColumn(
            _,
            "CalendarYear",
            each Date.Year([FullDate]),
            Int64.Type
        )
let
    // =========================================================================
    // Enterprise Financial Analytics Platform (EFAP)
    // Object: Dim_Date
    // Version: 1.0.0
    // =========================================================================
    // -------------------------------------------------------------------------
    // Configuration
    // -------------------------------------------------------------------------
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2035, 12, 31),
    FiscalYearStartMonth = 1,
    // -------------------------------------------------------------------------
    // Calendar
    // -------------------------------------------------------------------------
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, NumberOfDays, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(Dates, Splitter.SplitByNothing(), {"FullDate"}),
    // -------------------------------------------------------------------------
    // Basic Date Attributes
    // -------------------------------------------------------------------------
    AddDateKey = Table.AddColumn(
        DateTable,
        "DateKey",
        each Date.Year([FullDate]) * 10000 + Date.Month([FullDate]) * 100 + Date.Day([FullDate]),
        Int64.Type
    ),
    AddDay = Table.AddColumn(AddDateKey, "Day", each Date.Day([FullDate]), Int64.Type),
    AddDayName = Table.AddColumn(AddDay, "DayName", each Date.DayOfWeekName([FullDate]), type text),
    AddDayOfWeek = Table.AddColumn(
        AddDayName, "DayOfWeek", each Date.DayOfWeek([FullDate], Day.Monday) + 1, Int64.Type
    ),
    AddISOWeek = Table.AddColumn(AddDayOfWeek, "ISOWeek", each Date.WeekOfYear([FullDate], Day.Monday), Int64.Type),
    AddMonth = Table.AddColumn(AddISOWeek, "Month", each Date.Month([FullDate]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth, "MonthName", each Date.MonthName([FullDate]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each Date.QuarterOfYear([FullDate]), Int64.Type),
    AddQuarterName = Table.AddColumn(
        AddQuarter, "QuarterName", each "Q" & Text.From(Date.QuarterOfYear([FullDate])), type text
    ),
    AddYear = Table.AddColumn(AddQuarterName, "Year", each Date.Year([FullDate]), Int64.Type),
    // -------------------------------------------------------------------------
    // Fiscal Calendar
    // -------------------------------------------------------------------------
    AddFiscalMonth = Table.AddColumn(
        AddYear, "FiscalMonth", each Number.Mod(Date.Month([FullDate]) - FiscalYearStartMonth + 12, 12) + 1,
        Int64.Type
    ),
    AddFiscalQuarter = Table.AddColumn(
        AddFiscalMonth, "FiscalQuarter", each Number.RoundUp([FiscalMonth] / 3), Int64.Type
    ),
    AddFiscalYear = Table.AddColumn(
        AddFiscalQuarter,
        "FiscalYear",
        each if Date.Month([FullDate]) >= FiscalYearStartMonth then Date.Year([FullDate]) else Date.Year([FullDate]) - 1,
        Int64.Type
    ),
    // -------------------------------------------------------------------------
    // Flags
    // -------------------------------------------------------------------------
    AddWeekend = Table.AddColumn(AddFiscalYear, "IsWeekend", each [DayOfWeek] >= 6, type logical),
    AddWorkingDay = Table.AddColumn(AddWeekend, "IsWorkingDay", each not [IsWeekend], type logical),
    AddMonthEnd = Table.AddColumn(
        AddWorkingDay, "IsMonthEnd", each [FullDate] = Date.EndOfMonth([FullDate]), type logical
    ),
    AddQuarterEnd = Table.AddColumn(
        AddMonthEnd, "IsQuarterEnd", each [FullDate] = Date.EndOfQuarter([FullDate]), type logical
    ),
    AddYearEnd = Table.AddColumn(
        AddQuarterEnd, "IsYearEnd", each [FullDate] = Date.EndOfYear([FullDate]), type logical
    ),
    // -------------------------------------------------------------------------
    // Final Column Order
    // -------------------------------------------------------------------------
    Result = Table.ReorderColumns(
        AddYearEnd,
        {
            "DateKey",
            "FullDate",
            "Day",
            "DayName",
            "DayOfWeek",
            "ISOWeek",
            "Month",
            "MonthName",
            "Quarter",
            "QuarterName",
            "Year",
            "FiscalMonth",
            "FiscalQuarter",
            "FiscalYear",
            "IsWeekend",
            "IsWorkingDay",
            "IsMonthEnd",
            "IsQuarterEnd",
            "IsYearEnd"
        }
    )
in
    Result

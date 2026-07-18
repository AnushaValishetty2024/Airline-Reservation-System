document.addEventListener("DOMContentLoaded", function () {


    const occupancyChart =
        document.getElementById("occupancyChart");


    const performanceChart =
        document.getElementById("performanceChart");


    const flights =
        occupancyData.map(
            item => item.flight
        );


    const occupancy =
        occupancyData.map(
            item => item.occupancy
        );


    const booked =
        occupancyData.map(
            item => item.booked
        );



    // Occupancy Comparison Chart

    new Chart(
        occupancyChart,
        {

            type: "bar",

            data: {

                labels: flights,

                datasets: [

                    {
                        label: "Occupancy %",
                        data: occupancy
                    }

                ]

            },

            options: {

                responsive: true,

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100

                    }

                }

            }

        });



    // Flight Performance Chart

    new Chart(
        performanceChart,
        {

            type: "line",

            data: {

                labels: flights,

                datasets: [

                    {

                        label: "Booked Seats",

                        data: booked

                    }

                ]

            },

            options: {

                responsive: true

            }

        });



});
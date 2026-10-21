export default function About() {
  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Page Header */}
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-acten-gold">About ACTEN</h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto">
            The Association of Catholic Trained Evangelizers in Nigeria.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">

          {/* Main Content */}
          <div className="md:col-span-2 space-y-12">

            <section>
              <h2 className="font-serif text-3xl font-bold text-acten-green mb-4 border-b pb-2">Our Mission</h2>
              <p className="text-lg leading-relaxed text-gray-700 italic border-l-4 border-acten-gold pl-4 py-2 bg-acten-ivory/50">
                “To promote the evangelization mission of the Catholic Church in Nigeria by documenting, communicating, and supporting activities that proclaim Jesus Christ, strengthen Christian faith, encourage discipleship, and bring the Gospel to individuals, families, and communities.”
              </p>
            </section>

            <section>
              <h2 className="font-serif text-3xl font-bold text-acten-green mb-4 border-b pb-2">Our Vision</h2>
              <p className="text-lg leading-relaxed text-gray-700 italic border-l-4 border-acten-burgundy pl-4 py-2 bg-acten-ivory/50">
                “A vibrant community of trained Catholic evangelizers in Nigeria, committed to proclaiming the Gospel, nurturing Christian faith, and witnessing to Christ in every part of society.”
              </p>
            </section>

            <section>
              <h2 className="font-serif text-3xl font-bold text-acten-green mb-4 border-b pb-2">Introduction & Identity</h2>
              <div className="prose prose-lg max-w-none text-gray-700">
                <p>
                  The Association of Catholic Trained Evangelizers in Nigeria (ACTEN) is a dedicated body focused on the evangelization activities of the Catholic Church across the nation. We serve as a professional platform to highlight, coordinate, and support the diverse missionary and outreach efforts occurring within our dioceses and parishes.
                </p>
                <p>
                  Our members include trained lay evangelizers, catechists, religious, and clergy who are actively engaged in bringing the message of the Gospel to all corners of society, in accordance with the teachings and guidance of the Catholic Church.
                </p>
              </div>
            </section>

            <section>
              <h2 className="font-serif text-3xl font-bold text-acten-green mb-4 border-b pb-2">History & Founding</h2>
              <div className="prose prose-lg max-w-none text-gray-700">
                <p>
                  [History of ACTEN to be provided by leadership. This section will contain the story of how the association was formed, key milestones, and its growth across Nigeria.]
                </p>
              </div>
            </section>

            <section>
              <h2 className="font-serif text-3xl font-bold text-acten-green mb-4 border-b pb-2">Objectives</h2>
              <ul className="list-disc pl-6 space-y-2 text-lg text-gray-700">
                <li>To document and share news of Catholic evangelization activities across Nigeria.</li>
                <li>To provide formation and resources for evangelizers.</li>
                <li>To foster collaboration among diocesan and parish evangelization teams.</li>
                <li>To utilize digital media and modern platforms for Gospel proclamation.</li>
                <li>To support grassroots missions and community outreach programs.</li>
              </ul>
            </section>

          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <div className="bg-acten-ivory p-6 rounded-lg border border-gray-200">
              <h3 className="font-serif text-xl font-bold text-acten-green mb-4">Leadership</h3>
              <p className="text-sm text-gray-600 mb-4">
                The national leadership and spiritual chaplaincy information will be published once officially confirmed by ACTEN authorities.
              </p>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gray-300 rounded-full flex-shrink-0"></div>
                  <div>
                    <h4 className="font-bold">National President</h4>
                    <p className="text-sm text-gray-500">[To be updated]</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gray-300 rounded-full flex-shrink-0"></div>
                  <div>
                    <h4 className="font-bold">Spiritual Director</h4>
                    <p className="text-sm text-gray-500">[To be updated]</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-acten-ivory p-6 rounded-lg border border-gray-200">
              <h3 className="font-serif text-xl font-bold text-acten-green mb-4">Organizational Structure</h3>
              <p className="text-gray-700 mb-4">
                ACTEN operates through a coordinated network of national, provincial, and diocesan chapters to ensure effective evangelization at the grassroots level.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-acten-gold"></span> National Executive Council</li>
                <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-acten-gold"></span> Provincial Coordinators</li>
                <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-acten-gold"></span> Diocesan Leadership</li>
                <li className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-acten-gold"></span> Parish Units</li>
              </ul>
            </div>

             <div className="bg-acten-green text-acten-ivory p-6 rounded-lg">
              <h3 className="font-serif text-xl font-bold text-acten-gold mb-2">Join Our Mission</h3>
              <p className="text-sm opacity-90 mb-4">
                Are you a trained Catholic evangelizer? Connect with your local diocesan chapter to participate in our activities.
              </p>
              <a href="/contact" className="block text-center w-full py-2 bg-acten-gold text-acten-green font-bold rounded hover:bg-yellow-600 transition-colors">
                Contact Us
              </a>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
